"""
FastAPI 应用入口

启动命令 (在项目根目录):
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# 加载环境变量（在任何其他导入之前）
load_dotenv()

from db.database import init_db, SessionLocal
from db.models import User, Conversation, Message, DeviceRecord  # 确保模型被导入
from db.crud import import_csv_to_db
from api.auth import router as auth_router
from api.conversation import router as conversation_router
from api.chat import router as chat_router
from utils.logger_hander import logger
from utils.path_tool import get_abs_path


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    启动时: 初始化数据库、导入 CSV 数据
    关闭时: 清理资源
    """
    logger.info("=" * 50)
    logger.info("[启动] 智扫通机器人智能客服 - 后端服务启动中...")

    # 初始化数据库表
    init_db()
    logger.info("[启动] 数据库表初始化完成")

    # 导入 CSV 数据（如果尚未导入）
    try:
        db = SessionLocal()
        csv_path = get_abs_path("data/external/records.csv")
        import_csv_to_db(db, csv_path)
        db.close()
    except Exception as e:
        logger.warning(f"[启动] CSV 数据导入跳过或失败: {str(e)}")

    # 预加载 Agent（首次请求无需等待初始化）
    try:
        from agent.react_agent import get_agent
        get_agent()
        logger.info("[启动] Agent 预加载完成")
    except Exception as e:
        logger.warning(f"[启动] Agent 预加载失败（将在首次请求时初始化）: {str(e)}")

    logger.info("[启动] 后端服务启动完成!")
    logger.info("=" * 50)

    yield

    # 关闭时清理
    logger.info("[关闭] 后端服务正在关闭...")


# 创建 FastAPI 应用
app = FastAPI(
    title="智扫通机器人智能客服 API",
    description="基于 ReAct Agent 的智能客服后端，支持 RAG 知识问答、使用报告生成、天气查询等功能",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS 中间件（允许前端跨域请求）
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",    # Vite 开发服务器
        "http://localhost:3000",    # 备用端口
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth_router)
app.include_router(conversation_router)
app.include_router(chat_router)


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"[全局异常] {request.method} {request.url} - {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "服务器内部错误，请稍后重试"},
    )


# 健康检查接口
@app.get("/api/health", tags=["系统"])
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "智扫通机器人智能客服"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
