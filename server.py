import os
import pickle
import numpy as np
import httpx
import logging
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# ==========================================
# 日志配置 (Logging Configuration)
# ==========================================
# 配置日志格式，包含时间、日志级别和消息内容
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# ==========================================
# 配置参数 (Configuration)
# ==========================================
API_KEY = os.getenv("SILICONFLOW_API_KEY")
BASE_URL = os.getenv("SILICONFLOW_BASE_URL")
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-ai/DeepSeek-V3")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "Qwen/Qwen3-Embedding-0.6B")
APP_PORT = int(os.getenv("APP_PORT", 8000))
KNOWLEDGE_FILE = "data/knowledge.pkl"
SYSTEM_PROMPT_FILE = "System_prompt.txt"
TOP_K = 3
HISTORY_LIMIT = 10  # 保留的历史对话轮数

if not API_KEY:
    logger.warning("⚠️ 未在环境变量中找到 SILICONFLOW_API_KEY，服务可能无法正常调用 LLM。")

# ==========================================
# 数据模型 (Data Models)
# ==========================================
class ChatRequest(BaseModel):
    """
    聊天请求的数据模型
    """
    query: str = Field(..., min_length=1, max_length=2000, description="用户的查询文本")
    session_id: str = Field(..., min_length=1, max_length=100, description="唯一的会话标识符")
    new_session: Optional[bool] = False # 如果为 True，则清空该会话的历史记录

class ChatResponse(BaseModel):
    """
    聊天响应的数据模型
    """
    response: str

# ==========================================
# 核心组件 (Core Components)
# ==========================================
class KnowledgeBase:
    """
    知识库管理类：负责加载和检索向量数据
    """
    def __init__(self, filepath: str):
        self.chunks = []
        self.matrix = None
        self.load_data(filepath)
    
    def load_data(self, filepath: str):
        """加载本地的 pickle 向量文件"""
        if not os.path.exists(filepath):
            logger.warning(f"⚠️ 知识库文件 {filepath} 未找到。系统将以空知识库启动。")
            return
            
        try:
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
            
            self.chunks = data
            if data:
                # 创建 numpy 矩阵
                vectors = [item['vector'] for item in data]
                self.matrix = np.array(vectors).astype('float32')
                
                # 归一化向量 (L2 norm)，用于余弦相似度计算
                norms = np.linalg.norm(self.matrix, axis=1, keepdims=True)
                self.matrix = self.matrix / (norms + 1e-10) # 防止除以零
                
                logger.info(f"✅ 成功加载 {len(self.chunks)} 个知识块。")
            else:
                logger.warning("⚠️ 知识库文件是空的。")
        except Exception as e:
            logger.error(f"❌ 加载知识库失败: {e}")

    def search(self, query_vector: List[float], top_k: int = 3) -> List[Dict]:
        """根据查询向量检索最相似的 K 个片段"""
        if self.matrix is None or len(self.chunks) == 0:
            return []
            
        q_vec = np.array(query_vector).astype('float32')
        q_norm = np.linalg.norm(q_vec)
        q_vec = q_vec / (q_norm + 1e-10)
        
        # 计算余弦相似度: 归一化向量的点积
        scores = np.dot(self.matrix, q_vec)
        
        # 获取分数最高的 Top K 索引
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            # 简单的阈值过滤，分数大于 0.2 才认为是相关
            if scores[idx] > 0.2: 
                results.append(self.chunks[idx])
                
        return results

class SessionManager:
    """
    会话管理类：简单的内存存储，用于保存用户对话历史
    """
    def __init__(self):
        self.sessions: Dict[str, List[Dict[str, str]]] = {}
    
    def add_message(self, session_id: str, role: str, content: str):
        """添加一条消息到历史记录"""
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        
        self.sessions[session_id].append({"role": role, "content": content})
        
        # 截断历史，只保留最近的 N 轮
        if len(self.sessions[session_id]) > HISTORY_LIMIT * 2: 
            self.sessions[session_id] = self.sessions[session_id][-HISTORY_LIMIT:]
            
    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        """获取指定会话的历史记录"""
        return self.sessions.get(session_id, [])

    def clear_session(self, session_id: str):
        """清空指定会话的历史记录"""
        if session_id in self.sessions:
            del self.sessions[session_id]

# ==========================================
# 服务初始化 (Service Initialization)
# ==========================================
kb = KnowledgeBase(KNOWLEDGE_FILE)
sessions = SessionManager()
app = FastAPI(title="Lightweight RAG Agent")

# 安全配置: 添加 CORS 中间件
# 允许跨域请求，这对于前端开发调试非常重要
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中建议修改为具体的前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 辅助函数 (Helper Functions)
# ==========================================
async def get_embedding(text: str) -> List[float]:
    """调用外部 API 获取文本的 Embedding 向量"""
    url = f"{BASE_URL}/embeddings"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": EMBEDDING_MODEL,
        "input": text,
        "encoding_format": "float"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()['data'][0]['embedding']
        except Exception as e:
            logger.error(f"❌ 获取 Embedding 失败: {e}")
            raise e

async def call_llm(messages: List[Dict[str, str]]) -> str:
    """调用 LLM 进行对话生成，支持多模型自动降级"""
    url = f"{BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 从环境变量解析模型列表 (逗号分隔)
    models = [m.strip() for m in LLM_MODEL.split(',')]
    
    last_exception = None
    
    async with httpx.AsyncClient() as client:
        for model in models:
            try:
                logger.info(f"🔄 尝试调用 LLM 模型: {model}...")
                payload = {
                    "model": model,
                    "messages": messages,
                    "stream": False,
                    "temperature": 0.7
                }
                
                response = await client.post(url, json=payload, headers=headers, timeout=60.0)
                
                # 如果是服务端错误 (5xx)，抛出异常以触发重试
                if response.status_code >= 500:
                    response.raise_for_status()
                    
                # 如果成功 (200)
                if response.status_code == 200:
                    logger.info(f"✅ 模型 {model} 调用成功。")
                    return response.json()['choices'][0]['message']['content']
                
                # 如果是客户端错误 (4xx)，可能请求有问题，不再重试其他模型
                response.raise_for_status()
                
            except Exception as e:
                logger.error(f"❌ 模型 {model} 调用失败: {e}")
                last_exception = e
                continue
                
    # 如果所有模型都失败了
    if last_exception:
        raise last_exception
    raise Exception("所有 LLM 模型均调用失败")

def load_system_prompt():
    """从文件加载系统提示词"""
    try:
        with open(SYSTEM_PROMPT_FILE, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        logger.warning(f"⚠️ 无法加载系统提示词文件 {SYSTEM_PROMPT_FILE}: {e}。将使用默认提示词。")
        return "You are a helpful assistant."

# ==========================================
# API 路由 (API Routes)
# ==========================================
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    处理聊天请求的主入口
    """
    try:
        logger.info(f"📨 收到请求 - Session: {request.session_id}, Query: {request.query[:50]}...")

        # 0. 处理新会话标记
        if request.new_session:
            sessions.clear_session(request.session_id)
            logger.info(f"🔄 会话 {request.session_id} 已重置。")

        # 1. 获取用户问题的 Embedding
        logger.debug("正在获取查询向量...")
        query_vector = await get_embedding(request.query)
        
        # 2. 检索相关知识片段
        relevant_chunks = kb.search(query_vector, TOP_K)
        context_text = "\n\n".join([c['text'] for c in relevant_chunks])
        logger.info(f"📚 检索到 {len(relevant_chunks)} 个相关片段。")
        
        # 3. 构建包含历史记录和上下文的 Prompt
        base_prompt = load_system_prompt()
        system_prompt = f"""{base_prompt}

Context:
{context_text}
"""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # 添加历史记录
        history = sessions.get_history(request.session_id)
        messages.extend(history)
        
        # 添加当前问题
        messages.append({"role": "user", "content": request.query})
        
        # 4. 调用 LLM
        logger.debug("正在请求 LLM...")
        response_text = await call_llm(messages)
        
        # 5. 更新历史记录
        sessions.add_message(request.session_id, "user", request.query)
        sessions.add_message(request.session_id, "assistant", response_text)
        
        logger.info(f"📤 请求处理完成 - Session: {request.session_id}")
        return ChatResponse(response=response_text)
        
    except Exception as e:
        logger.error(f"❌ 处理请求时发生严重错误: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    logger.info(f"🚀 服务正在启动，监听端口: {APP_PORT}")
    uvicorn.run(app, host="0.0.0.0", port=APP_PORT)
