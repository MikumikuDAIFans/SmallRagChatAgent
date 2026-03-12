# Python RAG Agent 部署包 (Runtime Only)

本文件夹包含了在服务器上运行 RAG Agent 所需的最小文件集。

## 1. 目录结构
```text
.
├── .env.example       # 环境变量配置模板
├── Dockerfile         # Docker 构建文件
├── README.md          # 本文档
├── server.py          # 服务端主程序
├── System_prompt.txt  # 系统提示词 (可动态修改)
├── start.sh           # Linux 一键启动脚本
├── requirements.txt   # Python 依赖
└── data/              # 知识库目录
    └── knowledge.pkl  # 向量数据库文件
```

## 2. 快速部署 (Linux)

### 步骤 1: 准备环境
确保服务器已安装 Docker。

### 步骤 2: 配置 API Key
复制配置模板并编辑：
```bash
cp .env.example .env
nano .env
```
填入您的 `SILICONFLOW_API_KEY`。
*   `LLM_MODEL`: 可配置多个模型，用逗号分隔（例如 `deepseek-ai/DeepSeek-V3,deepseek-ai/DeepSeek-V2.5`）。系统会优先使用第一个，若失败（超时或500错误）则自动尝试下一个。
*   `APP_PORT`: 服务运行端口（默认 11451）。

### 步骤 3: 启动服务
运行启动脚本：
```bash
chmod +x start.sh
./start.sh
```
该脚本会自动构建镜像并启动容器，同时挂载 `data` 目录和提示词文件。

## 3. 常用操作

### 更新知识库
由于此为纯运行环境，请在本地开发机生成新的 `knowledge.pkl`，然后覆盖服务器上的 `data/knowledge.pkl`。
覆盖文件后，重启容器以加载新数据：
```bash
docker restart rag-agent
```

### 修改系统提示词
直接编辑 `System_prompt.txt` 文件即可。服务会在每次请求时读取最新内容，**无需重启**。

### 查看日志
```bash
docker logs -f rag-agent
```

## 4. 接口说明

**Endpoint**: `POST /chat`

**Payload**:
```json
{
  "session_id": "unique_user_id",
  "query": "用户问题",
  "new_session": false
}
```
*   `new_session`: (可选) 设为 `true` 可清空该 Session 的历史记录。
