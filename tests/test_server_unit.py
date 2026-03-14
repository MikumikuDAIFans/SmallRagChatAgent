import io
import os
import pickle
import sys
import types
import unittest
from unittest.mock import patch


def install_test_stubs():
    if "numpy" not in sys.modules:
        numpy_module = types.ModuleType("numpy")
        numpy_module.ndarray = list
        numpy_module.array = lambda *args, **kwargs: []
        numpy_module.dot = lambda *args, **kwargs: []
        numpy_module.argsort = lambda *args, **kwargs: []
        numpy_module.linalg = types.SimpleNamespace(norm=lambda *args, **kwargs: 0.0)
        sys.modules["numpy"] = numpy_module

    if "httpx" not in sys.modules:
        httpx_module = types.ModuleType("httpx")

        class Request:
            def __init__(self, method, url):
                self.method = method
                self.url = url

        class HTTPStatusError(Exception):
            def __init__(self, message, request=None, response=None):
                super().__init__(message)
                self.request = request
                self.response = response

        class AsyncClient:
            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc, tb):
                return False

        httpx_module.Request = Request
        httpx_module.HTTPStatusError = HTTPStatusError
        httpx_module.AsyncClient = AsyncClient
        sys.modules["httpx"] = httpx_module

    if "dotenv" not in sys.modules:
        dotenv_module = types.ModuleType("dotenv")
        dotenv_module.load_dotenv = lambda: None
        sys.modules["dotenv"] = dotenv_module

    if "fastapi" not in sys.modules:
        fastapi_module = types.ModuleType("fastapi")

        class HTTPException(Exception):
            def __init__(self, status_code, detail):
                super().__init__(detail)
                self.status_code = status_code
                self.detail = detail

        class FastAPI:
            def __init__(self, *args, **kwargs):
                self.routes = []

            def add_middleware(self, *args, **kwargs):
                return None

            def post(self, *args, **kwargs):
                def decorator(func):
                    return func

                return decorator

        fastapi_module.FastAPI = FastAPI
        fastapi_module.HTTPException = HTTPException
        sys.modules["fastapi"] = fastapi_module

    if "fastapi.middleware" not in sys.modules:
        sys.modules["fastapi.middleware"] = types.ModuleType("fastapi.middleware")

    if "fastapi.middleware.cors" not in sys.modules:
        cors_module = types.ModuleType("fastapi.middleware.cors")
        cors_module.CORSMiddleware = object
        sys.modules["fastapi.middleware.cors"] = cors_module

    if "pydantic" not in sys.modules:
        pydantic_module = types.ModuleType("pydantic")

        class BaseModel:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)

        def Field(default=None, **kwargs):
            return default

        pydantic_module.BaseModel = BaseModel
        pydantic_module.Field = Field
        sys.modules["pydantic"] = pydantic_module


install_test_stubs()
_original_exists = os.path.exists
os.path.exists = lambda path: False if str(path).endswith("knowledge.pkl") else _original_exists(path)
import httpx
import server
os.path.exists = _original_exists


class Exploit:
    def __reduce__(self):
        return (eval, ("__import__('os').system('echo hacked')",))


class FakeResponse:
    def __init__(self, status_code, payload=None):
        self.status_code = status_code
        self._payload = payload or {}
        self.request = httpx.Request("POST", "https://example.com")

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                f"HTTP {self.status_code}", request=self.request, response=self
            )


class FakeAsyncClient:
    def __init__(self, responses, calls):
        self._responses = list(responses)
        self.calls = calls

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, *args, **kwargs):
        self.calls.append({"args": args, "kwargs": kwargs})
        response = self._responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


class ServerBehaviorTests(unittest.IsolatedAsyncioTestCase):
    async def test_call_llm_stops_retrying_after_4xx(self):
        calls = []
        response = FakeResponse(400, {"error": "bad request"})

        with patch.object(server, "LLM_MODEL", "model-a,model-b"), patch.object(
            server.httpx,
            "AsyncClient",
            return_value=FakeAsyncClient([response], calls),
        ):
            with self.assertRaises(httpx.HTTPStatusError):
                await server.call_llm([{"role": "user", "content": "hello"}])

        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["kwargs"]["json"]["model"], "model-a")

    async def test_call_llm_retries_on_5xx(self):
        calls = []
        responses = [
            FakeResponse(502),
            FakeResponse(200, {"choices": [{"message": {"content": "ok"}}]}),
        ]

        with patch.object(server, "LLM_MODEL", "model-a,model-b"), patch.object(
            server.httpx,
            "AsyncClient",
            return_value=FakeAsyncClient(responses, calls),
        ):
            result = await server.call_llm([{"role": "user", "content": "hello"}])

        self.assertEqual(result, "ok")
        self.assertEqual([call["kwargs"]["json"]["model"] for call in calls], ["model-a", "model-b"])


class SessionManagerTests(unittest.TestCase):
    def test_session_history_keeps_last_n_rounds(self):
        manager = server.SessionManager()

        for index in range(server.HISTORY_LIMIT + 2):
            manager.add_message("s1", "user", f"u{index}")
            manager.add_message("s1", "assistant", f"a{index}")

        history = manager.get_history("s1")
        self.assertEqual(len(history), server.HISTORY_LIMIT * 2)
        self.assertEqual(history[0]["content"], "u2")
        self.assertEqual(history[-1]["content"], f"a{server.HISTORY_LIMIT + 1}")


class KnowledgeLoadTests(unittest.TestCase):
    def test_restricted_unpickler_rejects_unsafe_classes(self):
        payload = pickle.dumps(Exploit())

        with self.assertRaises(pickle.UnpicklingError):
            server.load_restricted_pickle(io.BytesIO(payload))

    def test_validate_knowledge_data_normalizes_numeric_vectors(self):
        data = [{"text": "hello", "vector": [1, 2.5], "source": "doc.md"}]

        validated = server.validate_knowledge_data(data)

        self.assertEqual(validated[0]["vector"], [1.0, 2.5])


if __name__ == "__main__":
    unittest.main()
