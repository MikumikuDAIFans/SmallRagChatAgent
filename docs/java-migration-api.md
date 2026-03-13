# Java 迁移实现文档

本文档只说明 Java 迁移最关键的内容：

- 当前业务链路怎么跑
- 外部 API 怎么调，payload 长什么样
- 当前“向量数据库”实际是怎么实现的
- Java 版建议怎么落地

## 1. 项目本质

这个项目本质上是一个轻量 RAG 服务。

当前线上主流程只有一条：

1. 接收用户问题 `/chat`
2. 调用 SiliconFlow `embeddings` 接口生成问题向量
3. 在本地向量数据中做相似度检索
4. 拼接 `system prompt + context + history + query`
5. 调用 SiliconFlow `chat/completions`
6. 返回回答并更新会话上下文

当前代码入口：

- 在线服务：[server.py](/E:/pythonAgent/server.py)
- 离线入库：[scripts/ingest.py](/E:/pythonAgent/scripts/ingest.py)

## 2. 当前业务逻辑

### 2.1 在线问答流程

对应代码：[server.py](/E:/pythonAgent/server.py):249

执行顺序如下：

1. 接收请求体：`query`、`session_id`、`new_session`
2. 如果 `new_session=true`，清空当前会话历史
3. 调用 `POST /embeddings`，把 `query` 转成向量
4. 使用问题向量在本地知识库中检索 TopK
5. 过滤掉相似度小于等于 `0.2` 的片段
6. 读取 [System_prompt.txt](/E:/pythonAgent/System_prompt.txt)
7. 组装 `messages`
8. 调用 `POST /chat/completions`
9. 保存本轮 `user` / `assistant` 到内存会话
10. 返回：

```json
{
  "response": "LLM 最终回复"
}
```

### 2.2 离线入库流程

对应代码：[scripts/ingest.py](/E:/pythonAgent/scripts/ingest.py):107

执行顺序如下：

1. 扫描 `doc/*.md`
2. 按 Markdown 标题切片
3. 每个片段调用 `POST /embeddings`
4. 生成如下结构：

```json
{
  "text": "[标题1 > 标题2]\n正文内容",
  "vector": [0.12, -0.03, 0.56],
  "source": "FAQ-Connection.md"
}
```

5. 最终保存到 `data/knowledge.pkl`

## 3. 当前“向量数据库”实际情况

### 3.1 现在并不是真正的向量数据库

当前 Python 项目没有接 Pinecone、Milvus、Qdrant、pgvector 这类真正的向量数据库。

它现在的实现是：

1. 离线把知识片段写入 `data/knowledge.pkl`
2. 服务启动时加载 `knowledge.pkl`
3. 把所有 `vector` 组成一个 `numpy` 矩阵
4. 对 query 向量和知识向量做 L2 归一化
5. 用点积计算余弦相似度
6. 取 TopK=3，再做阈值过滤

对应代码：

- 加载向量文件：[server.py](/E:/pythonAgent/server.py):71
- 归一化矩阵：[server.py](/E:/pythonAgent/server.py):83
- 相似度计算：[server.py](/E:/pythonAgent/server.py):97

### 3.2 当前检索规则

Java 迁移时，第一版建议先保持一致：

| 项目 | 当前值 |
| :--- | :--- |
| 检索条数 | `TopK = 3` |
| 相似度算法 | 归一化后点积，等价于余弦相似度 |
| 阈值 | `score > 0.2` |
| 知识源文件 | `data/knowledge.pkl` |

### 3.3 Java 版向量数据库建议

Java 版不建议继续直接依赖 Python `pickle` 文件。

建议改成下面两种方案之一：

#### 方案 A：先做轻量迁移

把知识库转成 JSON 或数据库表，Java 服务自己加载并计算相似度。

建议最少字段：

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

缺点：

- 数据量上来后性能和维护性一般

#### 方案 B：直接接真正的向量数据库

建议 Java 版抽象成：

1. `EmbeddingClient` 生成 query 向量
2. `VectorStore` 做 ANN / cosine search
3. 可选增加 `RerankClient`
4. `PromptBuilder` 组装 prompt
5. `LlmClient` 调用聊天接口

这样后续要切换到 pgvector、Milvus、Qdrant 都比较容易。

## 4. 外部 API 调用说明

下面的 payload 以“当前项目实际用法 + Java 迁移建议”来写。

### 4.1 Chat Completions

官方文档：

- [SiliconFlow Chat Completions](https://docs.siliconflow.cn/cn/api-reference/chat-completions/chat-completions)

当前代码调用位置：

- [server.py](/E:/pythonAgent/server.py):189

当前项目实际使用的 payload：

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

当前项目实际依赖的请求头：

```http
Authorization: Bearer {SILICONFLOW_API_KEY}
Content-Type: application/json
```

当前项目实际读取的返回字段：

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

当前降级逻辑代码：

- [server.py](/E:/pythonAgent/server.py):197

### 4.2 Embeddings

官方文档：

- [SiliconFlow Create Embeddings](https://docs.siliconflow.cn/cn/api-reference/embeddings/create-embeddings)

当前代码调用位置：

- 在线生成 query 向量：[server.py](/E:/pythonAgent/server.py):167
- 离线生成知识向量：[scripts/ingest.py](/E:/pythonAgent/scripts/ingest.py):85

当前项目实际使用的 payload：

```json
{
  "model": "Qwen/Qwen3-Embedding-0.6B",
  "input": "需要向量化的文本",
  "encoding_format": "float"
}
```

当前项目实际读取的返回字段：

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

- 第一版仍然使用 `encoding_format = float`
- `input` 先保持单字符串，不必一开始就做批量
- 如果未来做批量入库，再切换成数组输入
- Embedding 维度不要写死，直接按返回结果存储

### 4.3 Rerank

官方文档：

- [SiliconFlow Create Rerank](https://docs.siliconflow.cn/cn/api-reference/rerank/create-rerank)

说明：

- 当前 Python 项目 **没有调用** rerank 接口
- 但 Java 迁移时我建议你预留这一层，因为它正好能改善“Embedding 召回后排序不准”的问题

适合接入的位置：

1. 先从向量库召回 TopN，例如 10~20 条
2. 再调用 `rerank`
3. 取 rerank 后前 3 条进入最终 prompt

推荐 payload 结构：

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

Java 版推荐接入方式：

- `Embedding` 负责粗召回
- `Rerank` 负责精排
- `LLM` 负责最终生成

如果你后面要把精度做上去，rerank 往往是最值得加的一层。

## 5. Java 迁移时的请求编排

### 5.1 最接近当前 Python 的编排

```text
用户请求
  -> /chat
  -> embeddings(query)
  -> 本地向量检索 Top3
  -> chat/completions(messages)
  -> 返回 response
```

### 5.2 更适合 Java 大项目的编排

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

第二种是我更推荐的 Java 版本。

## 6. Java 模块建议

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

## 7. Java 版最少要兼容的内容

如果要做到“迁移后行为基本一致”，最少要保证这些点不变：

1. `/chat` 请求和响应结构不变
2. 仍然使用 `session_id` 维护多轮上下文
3. Embedding 模型不变
4. LLM 模型配置和降级顺序不变
5. prompt 结构不变
6. TopK=3 不变
7. 相似度阈值 `0.2` 不变

## 8. 结论

这次迁移最核心的不是 FastAPI 改成 Spring Boot，而是把下面三层重新落好：

1. 外部 API 调用层：`embeddings`、`chat/completions`、可选 `rerank`
2. 向量检索层：从 `knowledge.pkl + numpy` 升级成 Java 可维护的向量存储方案
3. RAG 编排层：保证 query -> recall -> rerank -> prompt -> generate 这条链路稳定

如果只求最快迁移：

- 先复刻当前逻辑
- 再把 `knowledge.pkl` 改为 Java 可读的数据源

如果要做长期版本：

- 直接引入真正的向量数据库
- 同时预留 rerank 层
