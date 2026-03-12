# Python RAG Agent 使用指南

## 1. 部署指南

### 1.1 环境变量配置
在项目根目录创建 `.env` 文件（或在 Docker 启动时传入）：
```bash
SILICONFLOW_API_KEY=your_api_key_here
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
LLM_MODEL=deepseek-ai/DeepSeek-V3
EMBEDDING_MODEL=Qwen/Qwen3-Embedding-0.6B
```

### 1.2 Docker 部署 (推荐)
本项目采用**挂载卷 (Volume Mount)** 的方式运行，这样可以在不重启容器的情况下更新知识库和系统提示词。

**步骤 1: 构建镜像**
```bash
docker build -t rag-agent .
```
*注意：由于 `.dockerignore` 排除了 `data/` 和 `doc/`，构建出的镜像不包含知识库文件，必须挂载使用。*

**步骤 2: 运行容器**
```bash
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/System_prompt.txt:/app/System_prompt.txt \
  --env-file .env \
  --name rag-agent \
  rag-agent
```
*   `-v $(pwd)/data:/app/data`: 挂载本地 `data` 目录，容器可以直接读取最新的 `knowledge.pkl`。
*   `-v $(pwd)/System_prompt.txt:/app/System_prompt.txt`: 挂载系统提示词文件，便于随时修改。

## 2. 知识库更新流程

当您有新的文档 (`.md`) 需要添加到知识库时：

1.  将新的 Markdown 文件放入 `doc/` 目录。
2.  在本地运行 `scripts/ingest.py` 脚本生成新的向量文件：
    ```bash
    python scripts/ingest.py
    ```
    *此命令会读取 `doc/` 下的所有文件，生成 `data/knowledge.pkl`。*
3.  **重启服务** (以便加载新的 pickle 文件到内存)：
    ```bash
    docker restart rag-agent
    ```

## 3. 修改系统提示词

1.  编辑根目录下的 `System_prompt.txt` 文件。
2.  保存文件。
3.  由于提示词是每次请求时动态读取的（或建议重启以确保完全生效，视实现而定，当前实现为每次请求读取），您**不需要**重启容器即可生效。
    *   *注：当前 `server.py` 实现为每次请求读取文件，因此修改立即生效。*

## 4. API 接口文档

### POST /chat

用于发送对话请求。

**URL**: `http://<server-ip>:8000/chat`
**Content-Type**: `application/json`

**请求参数 (Request Body)**:

| 参数名 | 类型 | 必选 | 描述 |
| :--- | :--- | :--- | :--- |
| `query` | string | 是 | 用户的问题或指令。 |
| `session_id` | string | 是 | 会话标识符。用于维护多轮对话上下文。同一用户的连续对话应使用相同的 ID。 |
| `new_session` | boolean | 否 | 默认为 `false`。如果设置为 `true`，将在处理当前请求前清空该 `session_id` 的历史记录（用于页面刷新或开始新对话）。 |

**示例请求**:
```json
{
  "session_id": "user_123",
  "query": "你好",
  "new_session": true
}
```

**响应参数 (Response Body)**:

| 参数名 | 类型 | 描述 |
| :--- | :--- | :--- |
| `response` | string | AI 生成的回答内容。 |

*注：响应中不再包含参考文档片段。*

**示例响应**:
```json
{
  "response": "ArtiMaker 支持导入 SVG, DXF, JPG, PNG 等格式..."
}
```

## 5. 测试方法

### 5.1 使用交互式脚本
```bash
python scripts/interactive_client.py
```
该脚本会自动连接本地 8000 端口进行多轮对话测试。

### 5.2 使用 Curl
```bash
curl -X POST "http://127.0.0.1:8000/chat" \
     -H "Content-Type: application/json" \
     -d "{\"session_id\": \"test\", \"query\": \"你好\"}"
```
