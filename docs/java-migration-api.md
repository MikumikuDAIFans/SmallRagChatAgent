# Java 迁移实现文档

本文档聚焦 Java 迁移最关键的四件事：

- 当前 Python 服务的真实请求链路是什么
- 外部 API 具体怎么调用，payload/headers/响应字段要读哪些
- 当前“向量数据库”实际上是什么，不是什么
- Java 版本应该先兼容什么，再升级什么

## 1. 项目本质

这个项目本质上是一个轻量级 RAG 问答服务，而不是一个完整的 Agent 平台。

当前主链路只有一条：

1. 接收 `POST /chat`
2. 调用 SiliconFlow `embeddings` 生成 query 向量
3. 在本地知识数据中做相似度检索
4. 组装 `system prompt + context + history + query`
5. 调用 SiliconFlow `chat/completions`
6. 返回回答并写入内存会话

当前关键入口：

- 在线服务：[server.py](/E:/pythonAgent/server.py)
- 离线入库：[scripts/ingest.py](/E:/pythonAgent/scripts/ingest.py)

## 2. 当前 Python 服务真实行为

### 2.1 在线问答流程

`POST /chat` 的处理顺序如下：

1. 接收请求体字段：`query`、`session_id`、`new_session`
2. 若 `new_session=true`，清空该 `session_id` 的历史
3. 调用 `POST /embeddings` 将 `query` 转成向量
4. 在本地知识库中做 TopK 检索
5. 过滤掉相似度 `<= 0.2` 的候选片段
6. 读取 [System_prompt.txt](/E:/pythonAgent/System_prompt.txt)
7. 组装 `messages`
8. 调用 `POST /chat/completions`
9. 将本轮 `user` / `assistant` 追加到内存会话
10. 返回：

```json
{
  "response": "LLM 最终回复"
}
```

### 2.2 会话行为

当前服务的会话管理是“进程内内存会话”，不是 Redis，也不是数据库持久化。

这意味着：

- 只靠 `session_id` 关联上下文
- 服务重启后历史会全部丢失
- 多实例部署时，不同实例之间不会共享会话
- 当前实现只保留最近 `HISTORY_LIMIT=10` 轮，也就是最近 20 条消息（user + assistant）

Java 迁移时如果要先做“行为兼容”，这里建议先保持一致；如果要做生产版，再升级成 Redis 或数据库会话。

### 2.3 离线入库流程

离线脚本执行顺序如下：

1. 扫描 `doc/*.md`
2. 按 Markdown 标题切片
3. 每个片段调用 `POST /embeddings`
4. 产出如下结构：

```json
{
  "text": "[标题1 > 标题2]\n正文内容",
  "vector": [0.12, -0.03, 0.56],
  "source": "FAQ-Connection.md"
}
```

5. 最终写入 `data/knowledge.pkl`

## 3. 当前“向量数据库”实际情况

### 3.1 它现在不是一个真正的向量数据库

当前 Python 项目并没有接入 Pinecone、Milvus、Qdrant、pgvector 这类真正的向量数据库。

它当前的实现本质上是：

1. 离线把知识片段和 embedding 写进 `data/knowledge.pkl`
2. 服务启动时把文件整体加载到内存
3. 用 `numpy` 把所有 `vector` 组装成矩阵
4. 对 query 向量和知识向量都做 L2 归一化
5. 用点积计算余弦相似度
6. 取 TopK=3，再做阈值过滤

### 3.2 当前检索规则

Java 第一版如果目标是“迁移后行为基本一致”，建议保留：

| 项目 | 当前值 |
| :--- | :--- |
| 检索条数 | `TopK = 3` |
| 相似度算法 | 归一化后点积，等价于余弦相似度 |
| 阈值 | `score > 0.2` |
| 知识源文件 | `data/knowledge.pkl` |

### 3.3 `knowledge.pkl` 的约束与风险

当前仓库里的知识文件虽然叫 `knowledge.pkl`，但它并不是一个适合长期跨语言依赖的存储格式。

主要原因：

- `pickle` 是 Python 私有序列化格式，Java 不能直接安全复用
- `pickle` 天然不适合做对外交换格式
- 如果把不可信文件直接 `pickle.load`，存在反序列化风险

因此，Java 迁移建议把它视为“过渡期内部产物”，而不是长期契约。

## 4. Java 版向量存储建议

### 4.1 方案 A：轻量兼容迁移

先把知识库转成 JSON 或数据库表，Java 服务自行加载并计算相似度。

建议至少保留这些字段：

```json
{
  "id": "chunk_001",
  "source": "FAQ-Connection.md",
  "header_path": "FAQ > Connection",
  "content": "正文内容",
  "text": "[FAQ > Connection]\n正文内容",
  "embedding": [0.12, -0.03, 0.56]
}
```

优点：

- 最接近当前 Python 实现
- Java 迁移成本最低
- 易于对照现网行为排查问题

缺点：

- 数据量扩大后，检索性能和维护性都一般
- 仍然需要 Java 自己维护内存索引

### 4.2 方案 B：直接接真正的向量数据库

更推荐在 Java 中抽象成以下组件：

1. `EmbeddingClient` 负责生成 query 向量
2. `VectorStore` 负责 ANN / cosine search
3. `RerankClient` 负责精排，可选
4. `PromptBuilder` 负责拼接 prompt
5. `LlmClient` 负责调 LLM

这样后续切到 pgvector、Milvus、Qdrant 时不会重写整条链路。

## 5. 外部 API 调用说明

下面的 payload 以“当前项目实际依赖的最小字段”为准，不写那些当前代码没有用到的可选参数。

### 5.1 Chat Completions

官方文档：

- [SiliconFlow Chat Completions](https://docs.siliconflow.cn/cn/api-reference/chat-completions/chat-completions)

当前项目实际使用的请求头：

```http
Authorization: Bearer {SILICONFLOW_API_KEY}
Content-Type: application/json
```

当前项目实际发送的 payload：

```json
{
  "model": "deepseek-ai/DeepSeek-V3",
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

当前项目实际依赖的响应字段：

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

Java 迁移建议：

- 保留 `model`
- 保留 `messages`
- 保留 `stream=false`
- 保留 `temperature=0.7`
- 第一版先不要改 prompt 结构
- 保留“多个模型顺序降级”的逻辑
- 将 `4xx` 视为非重试错误，将 `5xx` / 网络错误视为可降级错误

对应代码位置：

- [server.py](/E:/pythonAgent/server.py)

### 5.2 Embeddings

官方文档：

- [SiliconFlow Create Embeddings](https://docs.siliconflow.cn/cn/api-reference/embeddings/create-embeddings)

当前项目实际使用的 payload：

```json
{
  "model": "Qwen/Qwen3-Embedding-0.6B",
  "input": "需要向量化的文本",
  "encoding_format": "float"
}
```

当前项目实际读取的响应字段：

```json
{
  "data": [
    {
      "embedding": [0.12, -0.03, 0.56]
    }
  ]
}
```

Java 迁移建议：

- 第一版继续使用 `encoding_format = float`
- `input` 先保持单字符串，不必一开始就做批量
- 后续如果需要批量入库，再切换成数组输入
- Embedding 维度不要写死，直接按返回值存储

### 5.3 Rerank

官方文档：

- [SiliconFlow Create Rerank](https://docs.siliconflow.cn/cn/api-reference/rerank/create-rerank)

现状说明：

- 当前 Python 项目 **没有接入** rerank
- 但 Java 迁移时很建议预留这层，因为它正好能改善“Embedding 召回后排序不准”的问题

推荐接入位置：

1. 先从向量库召回 TopN，例如 10~20 条
2. 再调用 `rerank`
3. 只把 rerank 后前 3 条送进最终 prompt

推荐 payload：

```json
{
  "model": "BAAI/bge-reranker-v2-m3",
  "query": "用户问题",
  "documents": [
    "候选片段1",
    "候选片段2",
    "候选片段3"
  ],
  "top_n": 3,
  "return_documents": true
}
```

职责建议：

- `Embedding` 负责粗召回
- `Rerank` 负责精排
- `LLM` 负责最终生成

如果后续目标是提升准确率，rerank 往往是最值得新增的一层。

## 6. Java 请求编排建议

### 6.1 最接近当前 Python 的编排

```text
用户请求
  -> /chat
  -> embeddings(query)
  -> 本地向量检索 Top3
  -> chat/completions(messages)
  -> 返回 response
```

### 6.2 更适合 Java 项目的编排

```text
用户请求
  -> /chat
  -> embeddings(query)
  -> vector search topN
  -> rerank(query, documents)
  -> prompt builder
  -> chat/completions(messages)
  -> 返回 response
```

如果目标是“先迁移再优化”，先走 6.1；如果目标是“直接做长期版本”，优先走 6.2。

## 7. Java 模块拆分建议

建议至少拆成下面几个模块：

| 模块 | 职责 |
| :--- | :--- |
| `ChatController` | 提供 `/chat` 接口 |
| `ChatService` | 编排完整 RAG 流程 |
| `EmbeddingClient` | 调用 SiliconFlow embeddings |
| `VectorStore` | 查询向量数据库或本地向量索引 |
| `RerankClient` | 调用 SiliconFlow rerank，可选 |
| `PromptBuilder` | 拼接 system/context/history/query |
| `LlmClient` | 调用 SiliconFlow chat/completions |
| `SessionStore` | 保存会话上下文 |

## 8. 第一版必须兼容的内容

如果要做到“迁移后行为基本一致”，至少保证下面这些点不要先变：

1. `/chat` 请求和响应结构不变
2. 仍然使用 `session_id` 维护多轮上下文
3. Embedding 模型不变
4. LLM 模型配置和降级顺序不变
5. prompt 拼接结构不变
6. TopK=3 不变
7. 相似度阈值 `0.2` 不变

## 9. 建议的迁移顺序

推荐按下面顺序做，而不是一开始就重构所有层：

1. 先把外部 API client 在 Java 中跑通
2. 再把知识文件从 `pickle` 换成 Java 可读格式
3. 然后复刻当前 `/chat` 行为
4. 最后再引入 rerank、Redis 会话、真正的向量数据库

这样风险最小，也最容易对照 Python 现网结果做回归。

## 10. 结论

这次迁移最核心的并不是 FastAPI 改成 Spring Boot，而是把下面三层重新落好：

1. 外部 API 调用层：`embeddings`、`chat/completions`、可选 `rerank`
2. 向量检索层：从 `knowledge.pkl + numpy` 升级成 Java 可维护的存储方案
3. RAG 编排层：保证 query -> recall -> rerank -> prompt -> generate 这条链路稳定

如果只求最快迁移：

- 先复刻当前逻辑
- 再把 `knowledge.pkl` 替换成 Java 可读数据源

如果目标是长期版本：

- 直接引入真正的向量数据库
- 同时预留 rerank 与持久化会话层
