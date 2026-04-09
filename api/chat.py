"""
聊天 API 路由 (SSE 流式响应)
"""
import json
import asyncio
import queue
import threading
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sse_starlette.sse import EventSourceResponse
from db.database import get_db, SessionLocal
from db import crud
from db.models import User
from schemas.chat import ChatRequest
from auth.dependencies import get_current_user
from agent.react_agent import get_agent
from utils.logger_hander import logger

router = APIRouter(prefix="/api/chat", tags=["聊天"])


@router.post("/{conversation_id}")
async def chat_stream(
    conversation_id: int,
    req: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    发送消息并以 SSE 流式返回 Agent 回复

    流程:
    1. 验证对话归属
    2. 将用户消息存入数据库
    3. 加载对话历史
    4. 调用 Agent 流式推理
    5. 通过 SSE 逐 token 返回给前端（真正的流式）
    6. 完整回复存入数据库
    """
    # 1. 验证对话归属
    conv = crud.get_conversation_by_id(db, conversation_id, current_user.id)
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="对话不存在")

    # 2. 保存用户消息
    crud.add_message(db, conversation_id, "user", req.message)

    # 3. 加载对话历史（用于多轮记忆）
    history_messages = crud.get_conversation_messages(db, conversation_id)
    history = [
        {"role": msg.role, "content": msg.content}
        for msg in history_messages[:-1]  # 排除刚插入的当前消息
    ]

    # 4. 如果是第一条消息，用消息内容更新对话标题
    if len(history_messages) == 1:
        title = req.message[:50] + ("..." if len(req.message) > 50 else "")
        crud.update_conversation_title(db, conversation_id, current_user.id, title)

    # 5. 真正的流式 SSE 返回
    # 使用 queue + thread 让同步的 Agent 生成器与异步的 SSE 响应协作
    async def event_generator():
        chunk_queue = queue.Queue()
        agent = get_agent()
        tool_db = SessionLocal()

        def run_agent():
            """在子线程中运行同步 Agent，逐 chunk 放入队列"""
            try:
                for chunk in agent.execute_stream(
                    query=req.message,
                    user_id=current_user.id,
                    user_city=current_user.city or "",
                    history=history,
                    db_session=tool_db,
                ):
                    chunk_queue.put(("chunk", chunk))
                chunk_queue.put(("done", None))
            except Exception as e:
                logger.error(f"[Chat] Agent 推理异常: {str(e)}", exc_info=True)
                chunk_queue.put(("error", str(e)))

        # 启动 Agent 线程
        agent_thread = threading.Thread(target=run_agent, daemon=True)
        agent_thread.start()

        full_response = []

        try:
            while True:
                # 非阻塞地从队列中取 chunk，每 100ms 检查一次
                try:
                    event_type, data = await asyncio.get_event_loop().run_in_executor(
                        None, lambda: chunk_queue.get(timeout=0.1)
                    )
                except queue.Empty:
                    continue

                if event_type == "chunk":
                    full_response.append(data)
                    yield {
                        "event": "message",
                        "data": json.dumps({"content": data}, ensure_ascii=False),
                    }

                elif event_type == "done":
                    # 完整回复存入数据库
                    complete_response = "".join(full_response).strip()
                    if complete_response:
                        crud.add_message(db, conversation_id, "assistant", complete_response)

                    yield {
                        "event": "done",
                        "data": json.dumps({"status": "completed"}, ensure_ascii=False),
                    }
                    break

                elif event_type == "error":
                    yield {
                        "event": "error",
                        "data": json.dumps({"error": f"推理出错: {data}"}, ensure_ascii=False),
                    }
                    break

        finally:
            tool_db.close()
            agent_thread.join(timeout=5)

    return EventSourceResponse(event_generator())
