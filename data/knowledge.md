# Python Agent 开发指南

## 1. 简介
这是一个轻量级的 Python Agent，旨在通过 RAG 技术提供知识问答服务。它设计用于低资源环境，如 1核 1.5G 内存的服务器。

## 2. 核心功能
### 2.1 知识检索
系统使用向量数据库进行语义检索。开发阶段预先生成向量，服务端仅进行只读检索，极大降低了内存开销。

### 2.2 上下文记忆
服务端维护一个简单的内存会话存储，能够记住用户在单次对话中的上下文信息。

## 3. 部署说明
### 3.1 Docker 部署
系统提供 Dockerfile，可以直接构建镜像运行。
建议命令：
```bash
docker build -t my-agent .
docker run -d -p 8000:8000 my-agent
```

### 3.2 环境变量
需要配置 SILICONFLOW_API_KEY 以访问 LLM 服务。

## 4. API 参考
### POST /chat
用于发送对话请求。
参数：
- query: 用户问题
- session_id: 会话ID

返回：
- response: AI 回复
- references: 参考文档片段
