# Small RAG Chat Agent

一个面向 ArtiMaker 帮助文档场景的轻量级 RAG 问答服务。

它的目标很明确：用尽量少的依赖提供一个可部署、可维护、可迁移的知识问答 API。当前实现基于 Python + FastAPI + SiliconFlow，支持离线知识入库、在线向量检索、多轮上下文和 Docker 部署。

## 项目特性

- 只暴露一个核心接口：`POST /chat`
- 使用 SiliconFlow `embeddings` 和 `chat/completions`
- 通过离线脚本生成知识库，减轻线上服务压力
- 支持基于 `session_id` 的短期多轮会话
- 适合作为独立服务运行，也适合作为 Java 迁移前的参考实现

## 工作原理

在线问答链路：

1. 客户端调用 `POST /chat`
2. 服务将 `query` 发送到 Embedding 接口生成向量
3. 服务在本地知识数据中做相似度检索
4. 服务组装 `system prompt + context + history + query`
5. 服务调用大模型接口生成回答
6. 服务返回 `response` 并更新当前会话历史

离线入库链路：

1. 将 Markdown 文档放入 `doc/`
2. 执行 `scripts/ingest.py`
3. 生成 `data/knowledge.pkl`
4. 重启服务加载新知识库

## 仓库结构

```text
.
├── server.py                  # 在线服务入口
├── requirements.txt           # Python 依赖
├── Dockerfile                 # Docker 构建文件
├── .env.example               # 环境变量模板
├── System_prompt.txt          # 系统提示词
├── scripts/                   # 入库、测试、压测脚本
├── doc/                       # 原始知识文档
├── data/                      # 运行期数据目录
├── docs/                      # 设计、使用、迁移文档
├── deploy_package/            # 精简部署包
├── CONTRIBUTING.md            # 贡献说明
├── SECURITY.md                # 安全问题上报说明
└── .github/                   # Issue、PR、CI 配置
```

## 快速开始

### 1. 配置环境变量

复制模板文件：

```bash
cp .env.example .env
```

至少需要配置以下变量：

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

## API 示例

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

## Docker 部署

构建镜像：

```bash
docker build -t rag-agent .
```

运行容器：

```bash
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/System_prompt.txt:/app/System_prompt.txt \
  --env-file .env \
  --name rag-agent \
  rag-agent
```

## 常用脚本

| 脚本 | 说明 |
| :--- | :--- |
| `scripts/ingest.py` | 根据 `doc/` 中的文档重建知识库 |
| `scripts/interactive_client.py` | 本地多轮对话测试 |
| `scripts/test_server.py` | 简单接口测试 |
| `scripts/load_test.py` | 并发压测 |
| `scripts/verify_update.py` | 更新后快速验证 |

## 文档

- [使用说明](docs/usage_guide.md)
- [架构设计](docs/architecture_design.md)
- [Java 迁移实现文档](docs/java-migration-api.md)
- [文档目录说明](docs/README.md)

## 开发与协作

- 提交代码前请至少运行一次基础校验
- 新增文档后请同步更新对应说明
- 对外接口变更时请同步更新 README 和迁移文档
- 贡献流程见 [CONTRIBUTING.md](CONTRIBUTING.md)

## 安全说明

- 不要提交 `.env`、真实密钥或生成后的 `knowledge.pkl`
- 如发现安全问题，请按 [SECURITY.md](SECURITY.md) 中的方式反馈

## 开源说明

当前仓库已经按开源项目结构整理，但还没有加入正式的 `LICENSE` 文件。  
如果你准备把它作为真正的开源项目公开发布，建议优先补充许可证，否则其他人默认没有合法的复制、修改和分发权限。
