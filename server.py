import builtins
import logging
import os
import pickle
from typing import Dict, List, Optional

import httpx
import numpy as np
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

API_KEY = os.getenv("SILICONFLOW_API_KEY")
BASE_URL = os.getenv("SILICONFLOW_BASE_URL")
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-ai/DeepSeek-V3")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "Qwen/Qwen3-Embedding-0.6B")
APP_PORT = int(os.getenv("APP_PORT", 8000))
KNOWLEDGE_FILE = "data/knowledge.pkl"
SYSTEM_PROMPT_FILE = "System_prompt.txt"
TOP_K = 3
HISTORY_LIMIT = 10
SAFE_PICKLE_BUILTINS = {"list", "dict", "tuple", "set", "str", "int", "float", "bool"}

if not API_KEY:
    logger.warning("SILICONFLOW_API_KEY is not configured. LLM calls may fail.")


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000, description="用户查询")
    session_id: str = Field(..., min_length=1, max_length=100, description="会话标识")
    new_session: Optional[bool] = False


class ChatResponse(BaseModel):
    response: str


class RestrictedKnowledgeUnpickler(pickle.Unpickler):
    """Allow only basic builtins when loading the local knowledge file."""

    def find_class(self, module, name):
        if module == "builtins" and name in SAFE_PICKLE_BUILTINS:
            return getattr(builtins, name)
        raise pickle.UnpicklingError(f"Forbidden pickle class: {module}.{name}")


def load_restricted_pickle(file_obj):
    return RestrictedKnowledgeUnpickler(file_obj).load()


def validate_knowledge_data(data) -> List[Dict[str, object]]:
    if not isinstance(data, list):
        raise ValueError("Knowledge data must be a list")

    validated: List[Dict[str, object]] = []
    for index, item in enumerate(data):
        if not isinstance(item, dict):
            raise ValueError(f"Knowledge item #{index} must be a dict")

        text = item.get("text")
        vector = item.get("vector")
        source = item.get("source")

        if not isinstance(text, str) or not text.strip():
            raise ValueError(f"Knowledge item #{index} has invalid text")
        if not isinstance(source, str) or not source.strip():
            raise ValueError(f"Knowledge item #{index} has invalid source")
        if not isinstance(vector, list) or not vector:
            raise ValueError(f"Knowledge item #{index} has invalid vector")
        if not all(isinstance(value, (int, float)) for value in vector):
            raise ValueError(f"Knowledge item #{index} vector must contain only numbers")

        validated.append(
            {
                "text": text,
                "vector": [float(value) for value in vector],
                "source": source,
            }
        )

    return validated


class KnowledgeBase:
    def __init__(self, filepath: str):
        self.chunks: List[Dict[str, object]] = []
        self.matrix: Optional[np.ndarray] = None
        self.load_data(filepath)

    def load_data(self, filepath: str):
        if not os.path.exists(filepath):
            logger.warning("Knowledge file %s not found. Starting with an empty KB.", filepath)
            return

        try:
            with open(filepath, "rb") as f:
                data = validate_knowledge_data(load_restricted_pickle(f))

            self.chunks = data
            if data:
                vectors = [item["vector"] for item in data]
                self.matrix = np.array(vectors, dtype="float32")
                norms = np.linalg.norm(self.matrix, axis=1, keepdims=True)
                self.matrix = self.matrix / (norms + 1e-10)
                logger.info("Loaded %s knowledge chunks.", len(self.chunks))
            else:
                logger.warning("Knowledge file is empty.")
        except Exception as e:
            logger.error("Failed to load knowledge base: %s", e)
            self.chunks = []
            self.matrix = None

    def search(self, query_vector: List[float], top_k: int = 3) -> List[Dict]:
        if self.matrix is None or not self.chunks:
            return []

        q_vec = np.array(query_vector, dtype="float32")
        q_norm = np.linalg.norm(q_vec)
        q_vec = q_vec / (q_norm + 1e-10)

        scores = np.dot(self.matrix, q_vec)
        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            if scores[idx] > 0.2:
                results.append(self.chunks[idx])
        return results


class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, List[Dict[str, str]]] = {}

    def add_message(self, session_id: str, role: str, content: str):
        if session_id not in self.sessions:
            self.sessions[session_id] = []

        self.sessions[session_id].append({"role": role, "content": content})

        # Keep the most recent N rounds, where each round has two messages.
        max_messages = HISTORY_LIMIT * 2
        if len(self.sessions[session_id]) > max_messages:
            self.sessions[session_id] = self.sessions[session_id][-max_messages:]

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        return self.sessions.get(session_id, [])

    def clear_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]


kb = KnowledgeBase(KNOWLEDGE_FILE)
sessions = SessionManager()
app = FastAPI(title="Lightweight RAG Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def get_embedding(text: str) -> List[float]:
    url = f"{BASE_URL}/embeddings"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": EMBEDDING_MODEL,
        "input": text,
        "encoding_format": "float",
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()["data"][0]["embedding"]
        except Exception as e:
            logger.error("Failed to get embedding: %s", e)
            raise


async def call_llm(messages: List[Dict[str, str]]) -> str:
    url = f"{BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    models = [model.strip() for model in LLM_MODEL.split(",") if model.strip()]
    last_exception: Optional[Exception] = None

    async with httpx.AsyncClient() as client:
        for model in models:
            try:
                logger.info("Trying LLM model: %s", model)
                payload = {
                    "model": model,
                    "messages": messages,
                    "stream": False,
                    "temperature": 0.7,
                }
                response = await client.post(url, json=payload, headers=headers, timeout=60.0)

                if response.status_code == 200:
                    logger.info("Model %s succeeded.", model)
                    return response.json()["choices"][0]["message"]["content"]

                if 400 <= response.status_code < 500:
                    logger.error(
                        "Model %s failed with non-retryable status %s.",
                        model,
                        response.status_code,
                    )
                    response.raise_for_status()

                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                logger.error("Model %s failed: %s", model, e)
                last_exception = e
                if 400 <= e.response.status_code < 500:
                    raise
                continue
            except Exception as e:
                logger.error("Model %s failed: %s", model, e)
                last_exception = e
                continue

    if last_exception:
        raise last_exception
    raise RuntimeError("All configured LLM models failed.")


def load_system_prompt():
    try:
        with open(SYSTEM_PROMPT_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        logger.warning("Failed to load system prompt %s: %s", SYSTEM_PROMPT_FILE, e)
        return "You are a helpful assistant."


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        logger.info("Received request - session=%s query=%s", request.session_id, request.query[:50])

        if request.new_session:
            sessions.clear_session(request.session_id)
            logger.info("Session %s reset.", request.session_id)

        query_vector = await get_embedding(request.query)
        relevant_chunks = kb.search(query_vector, TOP_K)
        context_text = "\n\n".join([chunk["text"] for chunk in relevant_chunks])
        logger.info("Retrieved %s relevant chunks.", len(relevant_chunks))

        base_prompt = load_system_prompt()
        system_prompt = f"""{base_prompt}

Context:
{context_text}
"""

        messages = [{"role": "system", "content": system_prompt}]
        history = sessions.get_history(request.session_id)
        messages.extend(history)
        messages.append({"role": "user", "content": request.query})

        response_text = await call_llm(messages)

        sessions.add_message(request.session_id, "user", request.query)
        sessions.add_message(request.session_id, "assistant", response_text)

        logger.info("Request completed - session=%s", request.session_id)
        return ChatResponse(response=response_text)
    except Exception as e:
        logger.error("Request handling failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting service on port %s", APP_PORT)
    uvicorn.run(app, host="0.0.0.0", port=APP_PORT)
