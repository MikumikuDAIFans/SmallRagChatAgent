# 轻量级 Python RAG Agent 架构设计与实现路径

## 1. 项目概述
构建一个基于 Docker 部署的轻量级 RAG（检索增强生成）Agent，利用硅基流动（SiliconFlow）API 提供 LLM 和 Embedding 能力。系统分为“开发端数据处理”和“服务端推理”两部分，以满足 1核 1.5G 内存的低资源服务器环境要求。

## 2. 系统架构

### 2.1 整体架构图
```mermaid
graph TD
    subgraph Dev[开发环境 (数据预处理)]
        Raw[Markdown 知识库] --> Splitter[Markdown 切分 (按章节)]
        Splitter --> EmbedAPI_Dev[Embedding API (Qwen)]
        EmbedAPI_Dev --> VectorFile[向量数据库文件 (knowledge.pkl)]
    end

    subgraph Server[服务器环境 (Docker 1C/1.5G)]
        VectorFile --> |Volume Mount| App[Agent 服务程序]
        User[用户 POST 请求] --> |Session ID + Query| App
        App --> EmbedAPI_Prod[Embedding API (Qwen)]
        App --> Search[向量检索 (Numpy)]
        Search --> Context[构建提示词 (RAG + History + SystemPrompt)]
        Context --> LLM_API[LLM API (DeepSeek-V3)]
        LLM_API --> Response[返回结果 (无引用)]
    end
```

### 2.2 核心模块
1.  **离线数据处理 (Ingestion)**:
    *   运行在本地开发机。
    *   负责读取文本、分块、调用 API 生成向量。
    *   将 文本块 + 向量 保存为单一文件（如 pickle 格式），上传至服务器。
    *   **优势**: 服务器无需进行繁重的文本处理，只需加载文件，极大降低内存占用。

2.  **在线服务 (Server)**:
    *   **Web 接口**: 提供简单的 POST API。
    *   **向量检索**: 使用 `numpy` 进行余弦相似度计算（避免安装 FAISS/Chroma 等重型库）。
    *   **上下文管理**: 基于内存的简单会话管理 (`Dict[SessionID, List[Messages]]`)，实现多轮对话记忆。
    *   **LLM 调用**: 封装硅基流动 API 调用，使用动态加载的 System Prompt。
    *   **数据挂载**: 知识库和 System Prompt 通过 Docker Volume 挂载，便于动态更新。

## 3. 技术栈选型 (极简原则)

*   **编程语言**: Python 3.9+ (Slim 版本)
*   **Web 框架**: `FastAPI` (高性能) + `Uvicorn` (ASGI 服务器)
    *   *备选*: 如果追求极致更小，可使用 Python 原生 `http.server`，但 FastAPI 开发效率和规范性更好，且开销可控。
*   **科学计算**: `numpy` (仅用于向量点积计算)
*   **网络请求**: `requests` (同步) 或 `httpx` (异步，推荐配合 FastAPI)
*   **数据存储**: `pickle` (Python 原生序列化，读取快)
*   **容器化**: Docker (`python:3.9-slim` 基础镜像)

## 4. 详细配置信息

*   **API Provider**: 硅基流动 (SiliconFlow)
*   **Base URL**: `https://api.siliconflow.cn/v1`
*   **API Key**: `sk-dawtgfnorzjqrlgxrzazcuhnrllrfgfydxufmbgayidqldpb`
*   **LLM Model**: `deepseek-ai/DeepSeek-V3`
*   **Embedding Model**: `Qwen/Qwen3-Embedding-0.6B`

## 5. 实现路径

### 阶段一：环境准备与项目初始化
1.  创建项目目录结构。
2.  编写 `requirements.txt` (仅包含 `fastapi`, `uvicorn`, `numpy`, `requests`, `python-dotenv`)。

### 阶段二：开发端数据处理脚本 (`scripts/ingest.py`)
1.  **功能**:
    *   读取本地 `.md` 知识文档。
    *   **Markdown 语义切分**: 识别 Markdown 标题 (`#`, `##`...)，按章节/段落进行切分，保留层级上下文（如 "标题1 > 标题2: 内容"）。
    *   批量调用 `Qwen/Qwen3-Embedding-0.6B` 接口获取向量。
    *   将 `List[{text, vector}]` 序列化保存为 `knowledge_base.pkl`。
2.  **产出**: 生成好的向量数据文件。

### 阶段三：服务端 Agent 开发 (`server.py`)
1.  **全局初始化**: 启动时加载 `knowledge_base.pkl` 到内存（Numpy Array）。
2.  **上下文管理**: 设计一个全局字典 `SESSIONS` 存储最近 N 轮对话。
3.  **检索逻辑**:
    *   接收用户 Query。
    *   调用 API 获取 Query 向量。
    *   计算 Query 向量与 知识库向量 的余弦相似度。
    *   取 Top-K (如 K=3) 相关文本块。
4.  **生成逻辑**:
    *   构建 Prompt: System Prompt + 检索到的上下文 + 历史对话 + 当前问题。
    *   调用 `deepseek-ai/DeepSeek-V3`。
5.  **API 接口**:
    *   Endpoint: `POST /chat`
86→    *   Payload: `{"query": "...", "session_id": "...", "new_session": true/false}`

### 阶段四：Docker 部署
1.  编写 `Dockerfile`。
2.  构建镜像并测试内存占用。
3.  编写启动脚本。

## 6. 目录结构预览

```text
/
├── server.py              # [服务端] API 服务主程序
├── scripts/
│   └── ingest.py          # [开发端] 数据处理脚本
├── requirements.txt       # 依赖列表
├── Dockerfile             # 构建文件
├── .env                   # 环境变量 (API Key)
├── docs/
│   ├── architecture_design.md
│   └── project_notes.md
└── data/
    └── knowledge.pkl      # 生成的向量库文件
```

## 7. API 接口定义

**POST /chat**

**Request Body:**
```json
{
  "session_id": "user_123",
  "query": "这个Agent怎么部署？",
  "new_session": false
}
```

**Response:**
```json
{
  "response": "您可以直接使用 Docker 进行部署..."
}
```
