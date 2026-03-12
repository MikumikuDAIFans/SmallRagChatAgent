# Java 迁移接口说明

本文档只保留 Java 迁移最需要的信息：业务流程、接口调用、关键数据结构。

## 1. 项目作用

这是一个轻量级 RAG 问答服务，面向 ArtiMaker 帮助文档场景。

整体流程很简单：

1. 接收用户问题。
2. 调用 Embedding 接口把问题转成向量。
3. 用问题向量在本地知识库中检索相关文档片段。
4. 把系统提示词、检索结果、历史对话、当前问题组装成 `messages`。
5. 调用 LLM 接口生成回答。
6. 返回最终文本，并把本轮对话写入会话上下文。

对应主代码：

- 在线服务：[server.py](/E:/pythonAgent/server.py)
- 离线入库：[scripts/ingest.py](/E:/pythonAgent/scripts/ingest.py)

## 2. 当前涉及的接口

### 2.1 对外接口

#### `POST /chat`

请求体：

```json
{
  "query": "ArtiMaker 支持哪些文件格式？",
  "session_id": "user_1001",
  "new_session": false
}
```

字段说明：

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `query` | string | 是 | 用户问题 |
| `session_id` | string | 是 | 会话 ID，用于多轮上下文 |
| `new_session` | boolean | 否 | 为 `true` 时先清空当前会话历史 |

响应体：

```json
{
  "response": "ArtiMaker 当前支持导入 SVG、DXF、JPG、PNG 等格式。"
}
```

代码位置：

- 请求模型：[server.py](/E:/pythonAgent/server.py):45
- 响应模型：[server.py](/E:/pythonAgent/server.py):53
- 接口入口：[server.py](/E:/pythonAgent/server.py):249

### 2.2 外部接口

#### `POST {BASE_URL}/embeddings`

用途：

- 在线问答时，为 `query` 生成向量。
- 离线入库时，为知识片段生成向量。

请求示例：

```json
{
  "model": "Qwen/Qwen3-Embedding-0.6B",
  "input": "需要向量化的文本",
  "encoding_format": "float"
}
```

返回中实际使用字段：

```json
{
  "data": [
    {
      "embedding": [0.12, -0.03, 0.56]
    }
  ]
}
```

代码位置：

- 在线调用：[server.py](/E:/pythonAgent/server.py):167
- 离线调用：[scripts/ingest.py](/E:/pythonAgent/scripts/ingest.py):85

#### `POST {BASE_URL}/chat/completions`

用途：

- 根据 prompt 和历史消息生成最终回答。

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

返回中实际使用字段：

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

代码位置：

- LLM 调用：[server.py](/E:/pythonAgent/server.py):189

## 3. 核心业务流程

### 3.1 在线问答流程

Java 迁移时，建议直接按下面顺序复刻：

1. 接收 `/chat` 请求。
2. 如果 `new_session=true`，先删除该 `session_id` 的历史记录。
3. 调用 Embedding 接口，生成当前问题向量。
4. 在本地知识库里做相似度检索。
5. 取 Top 3 结果，并过滤掉分数小于等于 `0.2` 的片段。
6. 读取 `System_prompt.txt`。
7. 将检索结果拼成 `Context`。
8. 组装 `messages = [system] + history + current user query`。
9. 调用 LLM 接口生成回答。
10. 把本轮 `user` 和 `assistant` 消息写回会话。
11. 返回 `response`。

关键代码位置：

- 检索逻辑：[server.py](/E:/pythonAgent/server.py):97
- 会话管理：[server.py](/E:/pythonAgent/server.py):120
- prompt 组装：[server.py](/E:/pythonAgent/server.py):271
- 主流程入口：[server.py](/E:/pythonAgent/server.py):249

### 3.2 离线入库流程

如果 Java 项目也要接管知识入库，可按下面逻辑迁移：

1. 扫描 `doc/*.md`。
2. 按 Markdown 标题切分文档。
3. 每个片段保留标题路径，例如：`[一级标题 > 二级标题]`。
4. 调用 Embedding 接口生成片段向量。
5. 保存为知识库文件，供在线服务加载。

关键代码位置：

- 切片逻辑：[scripts/ingest.py](/E:/pythonAgent/scripts/ingest.py):23
- 入库主流程：[scripts/ingest.py](/E:/pythonAgent/scripts/ingest.py):107

## 4. Java 迁移必须保持一致的规则

这些规则决定了当前 Python 服务的行为，Java 迁移时最好先保持一致：

| 规则 | 当前实现 |
| :--- | :--- |
| 唯一业务接口 | `POST /chat` |
| 检索条数 | `TopK = 3` |
| 相似度阈值 | `score > 0.2` |
| 会话方式 | 内存 `session_id -> message list` |
| prompt 结构 | `system prompt + context + history + current query` |
| 模型降级 | `LLM_MODEL` 支持逗号分隔，按顺序重试 |
| 提示词加载 | 每次请求重新读取 `System_prompt.txt` |
| 知识库来源 | `data/knowledge.pkl` |

补充说明：

- 会话当前不是持久化的，服务重启后会丢失。
- `knowledge.pkl` 是 Python `pickle` 格式，Java 不建议直接读取。
- Java 更适合把知识库改为 JSON、数据库或向量库。

## 5. 关键数据结构

### 5.1 `/chat` 请求

```json
{
  "query": "用户问题",
  "session_id": "唯一会话ID",
  "new_session": false
}
```

### 5.2 会话数据

```json
[
  {
    "role": "user",
    "content": "你好"
  },
  {
    "role": "assistant",
    "content": "您好，我是 ArtiMaker AI Assistant。"
  }
]
```

### 5.3 知识库单条记录

```json
{
  "text": "[标题1 > 标题2]\n正文内容",
  "vector": [0.12, -0.03, 0.56],
  "source": "FAQ-Connection.md"
}
```

## 6. Java 代码建议拆分

为了最快迁移，Java 侧建议至少拆成下面几个类：

| Java 模块 | 职责 |
| :--- | :--- |
| `ChatController` | 对外提供 `/chat` |
| `ChatService` | 编排完整问答流程 |
| `EmbeddingClient` | 调用 `/embeddings` |
| `LlmClient` | 调用 `/chat/completions` |
| `KnowledgeRepository` | 加载知识片段和向量 |
| `Retriever` | 计算相似度并返回 TopK |
| `PromptBuilder` | 组装 system/context/history/query |
| `SessionStore` | 管理会话上下文 |

## 7. 迁移优先级建议

建议按这个顺序做：

1. 先保证 `/chat` 接口请求和响应完全兼容。
2. 再复刻当前问答流程和检索规则。
3. 最后再优化存储，把 `pickle` 和内存会话替换成更适合 Java 的实现。
