# Python RAG 项目接口文档（Java 迁移版）

## 第一章：文档头信息

| 项目项 | 内容 |
| :--- | :--- |
| 文档名称 | Python RAG 项目接口文档（Java 迁移版） |
| 文档目标 | 帮助 Java 开发人员快速理解现有 Python 项目的接口、业务流程、数据结构、开发维护方式，并迁移到 Java 大项目 |
| 当前代码仓库 | `E:\pythonAgent` |
| 当前在线服务入口 | `server.py` |
| 当前知识入库脚本 | `tool/ingest.py` |
| 当前运行方式 | Docker 部署，FastAPI 提供 HTTP 接口 |
| 当前业务领域 | ArtiMaker 软件帮助问答 |
| 迁移关注点 | 接口兼容、RAG 检索逻辑保持一致、会话上下文迁移、知识库格式迁移 |

## 第二章：项目概述

### 2.1 一句话说明

这是一个面向 ArtiMaker 产品文档问答场景的轻量级 RAG 服务：先从本地知识库中检索相关文档片段，再调用 SiliconFlow 的大模型生成回答。

### 2.2 项目目标

1. 对外提供一个简单的问答接口，供前端或其他系统通过 HTTP 调用。
2. 支持短期多轮上下文记忆，通过 `session_id` 维持会话。
3. 将产品帮助文档预处理为向量文件，减轻线上服务运行压力。
4. 适配低资源服务器场景，当前设计偏“单体、轻依赖、少组件”。

### 2.3 核心功能清单

- `F-01` 问答接口：接收用户问题，返回模型回复。
- `F-02` 上下文会话：同一 `session_id` 下保留短期会话历史。
- `F-03` 知识检索：基于向量相似度从本地知识库召回相关片段。
- `F-04` LLM 生成：将系统提示词、知识上下文、历史消息、当前问题一起发送给 LLM。
- `F-05` 离线入库：将 `doc/` 下 Markdown 文档切分并转成 `knowledge.pkl`。

### 2.4 当前不在范围内的内容

- 用户认证与权限控制。
- 会话持久化存储。
- 管理后台。
- 文档引用高亮返回。
- 知识库热加载。

## 第三章：架构设计

### 3.1 技术栈

| 类别 | 当前实现 |
| :--- | :--- |
| 语言 | Python 3.9 |
| Web 框架 | FastAPI |
| HTTP 客户端 | `httpx`（在线服务），`requests`（离线入库） |
| 向量计算 | `numpy` |
| 配置加载 | `python-dotenv` |
| 知识库存储 | Python `pickle` 文件 |
| 容器部署 | Docker |

### 3.2 系统边界

系统本身只做三件事：

1. 加载本地知识库文件。
2. 调用 SiliconFlow 外部接口完成 Embedding 和 LLM 推理。
3. 对外暴露一个 `/chat` HTTP 接口。

### 3.3 目录与职责

| 路径 | 作用 |
| :--- | :--- |
| `server.py` | 在线服务主入口，定义数据模型、会话管理、检索逻辑、对外接口 |
| `tool/ingest.py` | 离线知识入库脚本，负责切分 Markdown 并调用 Embedding 接口 |
| `doc/` | 原始知识文档目录，当前共 26 份 Markdown 文档 |
| `data/knowledge.pkl` | 生成后的向量知识库文件 |
| `System_prompt.txt` | 系统提示词模板 |
| `.env` | 外部接口地址、模型名、端口等运行配置 |
| `Dockerfile` | 镜像构建文件 |
| `tool/interactive_client.py` | 交互式测试脚本 |
| `tool/load_test.py` | 并发压测脚本 |

### 3.4 当前接口清单

#### 3.4.1 项目对外提供的接口

| 接口 | 方法 | 说明 |
| :--- | :--- | :--- |
| `/chat` | `POST` | 唯一业务接口，执行完整 RAG 问答流程 |

说明：

- FastAPI 会自动生成 `/docs` 和 OpenAPI 文档，但这是框架附带能力，不属于业务接口。

#### 3.4.2 项目内部调用的外部接口

| 接口 | 方法 | 来源 | 用途 |
| :--- | :--- | :--- | :--- |
| `/embeddings` | `POST` | SiliconFlow | 为用户问题或知识片段生成向量 |
| `/chat/completions` | `POST` | SiliconFlow | 基于组装后的消息生成回复 |

### 3.5 接口详细说明

#### 3.5.1 对外接口：`POST /chat`

请求体：

```json
{
  "query": "ArtiMaker 支持哪些文件格式？",
  "session_id": "user_1001",
  "new_session": false
}
```

请求字段：

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `query` | string | 是 | 用户问题，长度 1 到 2000 |
| `session_id` | string | 是 | 会话标识，长度 1 到 100 |
| `new_session` | boolean | 否 | 是否清空当前会话历史，默认 `false` |

响应体：

```json
{
  "response": "ArtiMaker 当前支持导入 SVG、DXF、JPG、PNG 等格式。"
}
```

响应字段：

| 字段 | 类型 | 说明 |
| :--- | :--- | :--- |
| `response` | string | 模型返回的最终回答 |

错误响应：

```json
{
  "detail": "具体异常信息"
}
```

#### 3.5.2 外部接口：`POST {BASE_URL}/embeddings`

当前用途：

- 在线问答时，为用户 `query` 生成向量。
- 离线入库时，为知识片段 `chunk.text` 生成向量。

请求示例：

```json
{
  "model": "Qwen/Qwen3-Embedding-0.6B",
  "input": "需要向量化的文本",
  "encoding_format": "float"
}
```

返回示例关注字段：

```json
{
  "data": [
    {
      "embedding": [0.12, -0.03, 0.56]
    }
  ]
}
```

#### 3.5.3 外部接口：`POST {BASE_URL}/chat/completions`

当前用途：

- 根据系统提示词、知识上下文、历史消息和当前问题生成最终回答。

请求示例：

```json
{
  "model": "deepseek-ai/DeepSeek-V3.2",
  "messages": [
    {
      "role": "system",
      "content": "系统提示词 + Context"
    },
    {
      "role": "user",
      "content": "用户问题"
    }
  ],
  "stream": false,
  "temperature": 0.7
}
```

返回示例关注字段：

```json
{
  "choices": [
    {
      "message": {
        "content": "最终回复"
      }
    }
  ]
}
```

### 3.6 关键设计决策

| 决策 | 当前做法 | 迁移含义 |
| :--- | :--- | :--- |
| 知识库文件化 | 使用 `knowledge.pkl` 本地加载 | Java 不适合直接读取 Python pickle，建议迁移为 JSON、数据库或向量库 |
| 会话存内存 | `Dict[session_id, messages]` | 单实例可用，多实例会丢失共享能力，Java 迁移建议放 Redis |
| 检索轻量实现 | `numpy` 余弦相似度 | Java 早期可先保留同类实现，后续再替换向量引擎 |
| 模型容灾 | LLM 支持按逗号分隔的模型降级 | Java 版本建议保留同样的回退顺序 |
| Prompt 动态读取 | 每次请求读取 `System_prompt.txt` | 便于运营改提示词，Java 侧建议保留热更新能力 |

## 第四章：业务逻辑详解

### 4.1 在线问答主流程

`S-01` 客户端调用 `POST /chat`，传入 `query`、`session_id`、`new_session`。  
`S-02` 如果 `new_session=true`，先清空该会话的历史消息。  
`S-03` 调用 Embedding 接口，将当前问题转为向量。  
`S-04` 在本地知识库中做相似度检索，取 Top 3，且只保留分数大于 0.2 的片段。  
`S-05` 读取 `System_prompt.txt`，并拼接检索上下文 `Context`。  
`S-06` 取出该 `session_id` 的历史消息，追加当前用户问题，组成完整 `messages`。  
`S-07` 调用 Chat Completions 接口，若首选模型失败则按配置顺序继续尝试下一个模型。  
`S-08` 得到模型回复后，将本轮 user/assistant 消息写入内存会话，最后返回给调用方。  

### 4.2 离线入库流程

`S-09` 扫描 `doc/*.md` 文档。  
`S-10` 按 Markdown 标题层级切分文档，生成带标题路径的知识片段。  
`S-11` 对每个知识片段调用 Embedding 接口生成向量。  
`S-12` 将 `text + vector + source` 保存到 `data/knowledge.pkl`。  
`S-13` 服务重启后重新加载新知识库。  

### 4.3 业务规则表

| 编号 | 规则 | 代码定位 |
| :--- | :--- | :--- |
| `R-01` | 系统只有一个业务入口接口：`POST /chat` | `server.py` `chat()` |
| `R-02` | `new_session=true` 时必须先清空旧上下文，再处理本次请求 | `server.py` 第 257-260 行 |
| `R-03` | 当前查询必须先做 Embedding，不能直接拿原文检索 | `server.py` 第 262-264 行 |
| `R-04` | 检索时只取 Top 3 结果，并且相似度阈值是 `0.2` | `server.py` 第 97-118 行 |
| `R-05` | Prompt 结构固定为“系统提示词 + Context + 历史消息 + 当前问题” | `server.py` 第 271-286 行 |
| `R-06` | LLM 模型列表支持逗号分隔，按顺序降级重试 | `server.py` 第 197-230 行 |
| `R-07` | 会话只保存在进程内存中，服务重启后全部丢失 | `server.py` 第 120-145 行 |
| `R-08` | 系统提示词文件每次请求重新读取，因此修改文件可直接生效 | `server.py` 第 237-244 行 |
| `R-09` | 离线切片按 Markdown 标题层级拼出头部路径，例如 `[一级标题 > 二级标题]` | `tool/ingest.py` 第 23-83 行 |
| `R-10` | 入库结果结构至少包含 `text`、`vector`、`source` | `tool/ingest.py` 第 137-141 行 |

### 4.4 模块输入输出与异常处理

#### 4.4.1 `KnowledgeBase`

输入：

- `data/knowledge.pkl`
- 查询向量 `query_vector`

输出：

- 命中的知识片段列表

异常策略：

- 文件不存在时以空知识库启动。
- 文件损坏或解析失败时记录日志。

#### 4.4.2 `SessionManager`

输入：

- `session_id`
- `role`
- `content`

输出：

- 当前会话历史列表

异常策略：

- 无持久化、无锁、无过期机制。
- 当前适用于单进程轻量场景。

#### 4.4.3 `get_embedding`

输入：

- 文本内容

输出：

- 浮点向量数组

异常策略：

- 外部请求失败直接抛错，由上层统一返回 `500`。

#### 4.4.4 `call_llm`

输入：

- `messages`

输出：

- 模型回复文本

异常策略：

- 5xx 或超时会继续尝试下一个模型。
- 所有模型都失败时抛出最后一个异常。

## 第五章：数据设计

### 5.1 原始知识数据

来源目录：

- `doc/`

文件格式：

- Markdown

当前规模：

- 26 份产品帮助文档

### 5.2 知识切片结构

离线切片后的单条结构可抽象为：

```json
{
  "text": "[标题1 > 标题2]\n正文内容",
  "metadata": {
    "headers": {
      "1": "标题1",
      "2": "标题2"
    },
    "content": "正文内容"
  }
}
```

### 5.3 向量知识库结构

`knowledge.pkl` 中每条记录结构如下：

```json
{
  "text": "[标题1 > 标题2]\n正文内容",
  "vector": [0.12, -0.03, 0.56],
  "source": "FAQ-Connection.md"
}
```

说明：

- Python 代码使用 `pickle.dump(List[dict])` 序列化。
- 服务启动时会把全部 `vector` 读入 `numpy` 矩阵。

### 5.4 会话数据结构

内存结构如下：

```json
{
  "session_id_1": [
    {
      "role": "user",
      "content": "你好"
    },
    {
      "role": "assistant",
      "content": "您好，我是 ArtiMaker AI Assistant。"
    }
  ]
}
```

说明：

- 数据只存在内存，不落库。
- 当前代码达到阈值后只保留最后一段历史消息。
- 注释写的是保留 10 轮，但实际截断逻辑需要以代码行为为准。

### 5.5 环境配置项

| 配置项 | 说明 |
| :--- | :--- |
| `SILICONFLOW_API_KEY` | SiliconFlow 访问凭证 |
| `SILICONFLOW_BASE_URL` | 外部 API 地址，当前为 `https://api.siliconflow.cn/v1` |
| `LLM_MODEL` | 对话模型，可配置多个，用逗号分隔 |
| `EMBEDDING_MODEL` | 向量模型 |
| `APP_PORT` | 服务监听端口 |

### 5.6 Java 迁移时的数据建议

1. 不建议 Java 直接读取 `knowledge.pkl`。
2. 建议将离线知识数据改存为以下任一形式：
   - JSON Lines
   - MySQL / PostgreSQL 表
   - Elasticsearch
   - 向量数据库
3. 如果需要快速迁移，可先新增一个 Python 导出脚本，把 `knowledge.pkl` 转成 JSON，再由 Java 加载。

## 第六章：部署与运维指引

### 6.1 当前部署方式

当前项目使用 Docker 单容器部署。

核心构建逻辑：

- 以 `python:3.9-slim` 为基础镜像。
- 安装 `requirements.txt` 中的依赖。
- 拷贝项目代码。
- 启动命令为 `python server.py`。

### 6.2 当前部署步骤

构建镜像：

```bash
docker build -t rag-agent .
```

启动容器：

```bash
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/System_prompt.txt:/app/System_prompt.txt \
  --env-file .env \
  --name rag-agent \
  rag-agent
```

说明：

- `data/` 通过挂载提供知识库文件。
- `System_prompt.txt` 通过挂载支持在线调整。
- `.dockerignore` 已排除 `data/` 和 `doc/`，因此镜像内默认不带知识库与原始文档。

### 6.3 常见运维动作

#### 更新知识库

1. 更新 `doc/` 下的 Markdown 文档。
2. 执行：

```bash
python tool/ingest.py
```

3. 重新生成 `data/knowledge.pkl`。
4. 重启服务使新知识库生效。

#### 更新提示词

1. 修改 `System_prompt.txt`。
2. 无需重启服务即可生效，因为每次请求都会重新读取。

#### 查看日志

```bash
docker logs -f rag-agent
```

### 6.4 常见故障排查

| 现象 | 重点排查项 |
| :--- | :--- |
| `/chat` 返回 500 | `SILICONFLOW_API_KEY`、外部网络、模型名是否正确 |
| 检索不到内容 | `knowledge.pkl` 是否存在、是否重新生成、是否成功挂载 |
| 回答风格异常 | `System_prompt.txt` 是否被修改 |
| 多轮上下文失效 | `session_id` 是否变化、服务是否重启 |
| 线上结果与本地不同 | `.env` 配置、知识库版本、提示词版本是否一致 |

## 第七章：开发指引

### 7.1 本地开发启动

安装依赖：

```bash
pip install -r requirements.txt
```

启动服务：

```bash
python server.py
```

测试接口：

```bash
python tool/interactive_client.py
```

### 7.2 新增知识文档的标准做法

1. 将新文档放入 `doc/`。
2. 运行 `tool/ingest.py` 重建向量文件。
3. 重启服务。
4. 用测试脚本验证问答效果。

### 7.3 Java 迁移建议的模块拆分

建议 Java 版本至少拆为以下模块：

| Java 模块 | 对应职责 |
| :--- | :--- |
| `ChatController` | 对外暴露 `/chat` 接口 |
| `ChatService` | 编排完整问答流程 |
| `EmbeddingClient` | 调用 SiliconFlow `/embeddings` |
| `LlmClient` | 调用 SiliconFlow `/chat/completions` |
| `KnowledgeRepository` | 加载知识切片与向量 |
| `Retriever` | 计算相似度并返回 Top K |
| `PromptBuilder` | 拼接 system/context/history/query |
| `SessionStore` | 管理上下文，建议接 Redis |

### 7.4 Java 迁移优先级建议

1. 先保证 `/chat` 对外契约完全兼容。
2. 再复刻当前 RAG 流程：Embedding、TopK=3、阈值=0.2、Prompt 结构、模型降级顺序。
3. 最后再优化存储介质，把 `pickle` 和内存会话替换为更适合 Java 大项目的方案。

### 7.5 维护建议

1. 将提示词、模型名、阈值、TopK、会话长度都配置化。
2. 给外部接口调用增加超时、重试、熔断和告警。
3. 给知识库版本、提示词版本增加显式标识，方便排查线上问题。
4. 给 `/chat` 增加请求日志和 trace id，便于在 Java 大项目内联调。
5. 如果未来要多实例部署，会话必须迁移到 Redis 或数据库。

## 第八章：版本历史

| 版本 | 日期 | 说明 |
| :--- | :--- | :--- |
| `v1.0` | 2026-03-12 | 基于当前 Python 项目整理首版 Java 迁移接口文档 |
