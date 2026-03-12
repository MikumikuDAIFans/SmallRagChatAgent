# Small RAG Chat Agent

这是一个面向 ArtiMaker 帮助文档场景的轻量级 RAG 问答服务。

项目特点：

- 对外只提供一个 `POST /chat` 接口，便于前端或其他系统接入。
- 使用 SiliconFlow 提供的 Embedding 和 LLM 能力。
- 知识库在离线阶段预处理，线上只做加载、检索和问答。
- 支持基于 `session_id` 的短期多轮上下文。
- 适合先作为独立 Python 服务运行，再逐步迁移到 Java 大项目。

## 目录结构

```text
.
|-- server.py                 # 服务入口
|-- requirements.txt          # Python 依赖
|-- Dockerfile                # Docker 构建文件
|-- .env.example              # 环境变量模板
|-- .gitignore                # Git 忽略规则
|-- .dockerignore             # Docker 构建忽略规则
|-- System_prompt.txt         # 系统提示词
|-- data/                     # 运行期数据目录
|   `-- README.md             # 数据目录说明
|-- doc/                      # 原始知识文档（Markdown）
|-- scripts/                  # 入库、测试、压测脚本
|-- docs/                     # 项目文档与迁移文档
`-- deploy_package/           # 面向服务器部署的精简运行包
```

## 核心流程

在线问答流程：

1. 客户端调用 `POST /chat`。
2. 服务调用 Embedding 接口生成问题向量。
3. 服务从本地知识库检索相关片段。
4. 服务组装 `system prompt + context + history + query`。
5. 服务调用 LLM 接口生成回答。
6. 返回 `response`，并更新会话上下文。

离线入库流程：

1. 将知识文档放入 `doc/`。
2. 运行 `scripts/ingest.py`。
3. 生成 `data/knowledge.pkl`。
4. 重启服务后使用新知识库。

## 快速开始

### 1. 配置环境变量

复制模板：

```bash
cp .env.example .env
```

至少需要配置：

- `SILICONFLOW_API_KEY`
- `SILICONFLOW_BASE_URL`
- `LLM_MODEL`
- `EMBEDDING_MODEL`
- `APP_PORT`

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 启动服务

```bash
python server.py
```

### 4. 本地测试

```bash
python scripts/interactive_client.py
```

## 接口说明

### `POST /chat`

请求体：

```json
{
  "query": "ArtiMaker 支持哪些文件格式？",
  "session_id": "user_1001",
  "new_session": false
}
```

响应体：

```json
{
  "response": "ArtiMaker 当前支持导入 SVG、DXF、JPG、PNG 等格式。"
}
```

如果你只关心 Java 迁移，请直接看：

- [Java 迁移接口说明](/E:/pythonAgent/docs/java-migration-api.md)

## 常用脚本

| 脚本 | 作用 |
| :--- | :--- |
| `scripts/ingest.py` | 根据 `doc/` 文档重建知识库 |
| `scripts/interactive_client.py` | 本地多轮对话测试 |
| `scripts/test_server.py` | 简单请求测试 |
| `scripts/load_test.py` | 并发压测 |
| `scripts/verify_update.py` | 更新后快速验证 |

## 部署说明

推荐使用 Docker：

```bash
docker build -t rag-agent .
docker run -d -p 8000:8000 -v $(pwd)/data:/app/data -v $(pwd)/System_prompt.txt:/app/System_prompt.txt --env-file .env --name rag-agent rag-agent
```

补充说明：

- `data/knowledge.pkl` 是运行产物，默认不提交 Git。
- `.env` 为本地私密配置，默认不提交 Git。
- `System_prompt.txt` 会在每次请求时读取，修改后通常无需重启服务。
- `deploy_package/` 是面向服务器的精简运行包，适合单独拷贝部署。

## 文档索引

- [文档目录说明](/E:/pythonAgent/docs/README.md)
- [使用说明](/E:/pythonAgent/docs/usage_guide.md)
- [架构设计](/E:/pythonAgent/docs/architecture_design.md)
- [Java 迁移接口说明](/E:/pythonAgent/docs/java-migration-api.md)

## 提交说明

当前仓库已经整理为适合长期维护的结构：

- 业务代码保留在根目录和 `scripts/`
- 文档统一放在 `docs/`
- 运行数据统一放在 `data/`
- 部署包单独放在 `deploy_package/`

如果后续继续迭代，建议保持这个分层方式不再混放。
