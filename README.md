# 智扫通 · 智能扫地机器人客服系统

基于 **ReAct Agent + RAG** 构建的垂直领域智能客服系统，面向扫地机器人和扫拖一体机器人场景。

## 技术栈

| 层级 | 技术 |
|------|------|
| **Agent 框架** | LangChain + LangGraph (ReAct 架构) |
| **大语言模型** | 通义千问 qwen3-max |
| **向量数据库** | ChromaDB + text-embedding-v4 |
| **后端** | FastAPI + SQLAlchemy + MySQL |
| **前端** | React + Vite |
| **认证** | JWT (Access + Refresh Token) + bcrypt |
| **实时通信** | Server-Sent Events (SSE) |

## 核心功能

- 🤖 **ReAct 自主推理**：Agent 自主决策工具调用顺序，支持多步推理
- 📚 **RAG 知识问答**：基于 6 份专业文档的语义检索与回答生成
- 🌤️ **实时天气适配**：集成 WeatherAPI，结合用户城市给出使用建议
- 📊 **个性化报告**：查询用户设备使用记录，生成 Markdown 格式使用报告
- 💬 **多轮对话**：对话历史持久化，支持上下文连贯的多轮交互
- 🔐 **用户认证**：JWT 双令牌机制，接口级权限控制
- 🎨 **流式输出**：SSE 实时推送 + 前端打字机效果

## 快速启动

### 1. 环境准备

```bash
# Python 3.11+  |  Node.js 18+  |  MySQL 8.0+
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入你的 API Key 和数据库密码
```

### 3. 启动后端

```bash
# 安装依赖
pip install fastapi python-jose[cryptography] python-multipart pymysql sse-starlette

# 创建 MySQL 数据库
mysql -u root -p -e "CREATE DATABASE agent_db DEFAULT CHARSET utf8mb4;"

# 启动
uvicorn main:app --reload --port 8000
```

### 4. 启动前端

```bash
cd frontend
npm install
npm run dev
```

### 5. 访问

- 前端页面：http://localhost:5173
- API 文档：http://localhost:8000/docs

## 项目结构

```
AgentProject/
├── main.py                 # FastAPI 入口
├── .env                    # 环境变量（不入库）
├── agent/                  # Agent 核心
│   ├── react_agent.py      # ReAct Agent 引擎
│   └── tools/              # 工具 & 中间件
├── api/                    # API 路由
│   ├── auth.py             # 认证接口
│   ├── chat.py             # 聊天接口 (SSE)
│   └── conversation.py     # 对话管理
├── auth/                   # 认证模块 (JWT + bcrypt)
├── db/                     # 数据库 (SQLAlchemy + MySQL)
├── schemas/                # Pydantic 数据模型
├── rag/                    # RAG 检索服务
├── model/                  # 模型工厂
├── prompts/                # 提示词模板
├── config/                 # YAML 配置
├── utils/                  # 工具类
├── data/                   # 知识库文档
└── frontend/               # React 前端
    └── src/
        ├── pages/          # 认证页 + 聊天页
        ├── components/     # 侧边栏 + 消息 + 输入框
        ├── api/            # API 调用封装
        └── context/        # Auth 状态管理
```

## License

MIT
