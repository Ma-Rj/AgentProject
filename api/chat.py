"""
聊天 API 路由 (SSE 流式响应)
"""
import json
import asyncio
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
    5. 通过 SSE 逐块返回给前端
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
        for msg in history_messages[:-1]  # 排除刚插入的当前消息（agent 中会单独添加）
    ]

    # 4. 如果是第一条消息，用消息内容更新对话标题
    if len(history_messages) == 1:
        title = req.message[:50] + ("..." if len(req.message) > 50 else "")
        crud.update_conversation_title(db, conversation_id, current_user.id, title)

    # 5. SSE 流式返回
    async def event_generator():
        full_response = []
        agent = get_agent()

        # 使用独立的 DB session 供 Agent 工具查询（避免和请求 session 冲突）
        tool_db = SessionLocal()

        try:
            # 在线程池中运行同步的 Agent 生成器
            loop = asyncio.get_event_loop()

            def run_agent():
                return list(agent.execute_stream(
                    query=req.message,
                    user_id=current_user.id,
                    user_city=current_user.city or "",
                    history=history,
                    db_session=tool_db,
                ))

            # 同步 Agent 在线程中执行，逐块产出
            chunks = await loop.run_in_executor(None, run_agent)

            for chunk in chunks:
                full_response.append(chunk)
                yield {
                    "event": "message",
                    "data": json.dumps({"content": chunk}, ensure_ascii=False),
                }

            # 6. 完整回复存入数据库
            complete_response = "".join(full_response).strip()
            if complete_response:
                # 使用请求的 DB session 保存消息
                crud.add_message(db, conversation_id, "assistant", complete_response)

            yield {
                "event": "done",
                "data": json.dumps({"status": "completed"}, ensure_ascii=False),
            }

        except Exception as e:
            logger.error(f"[Chat] Agent 推理异常: {str(e)}", exc_info=True)
            yield {
                "event": "error",
                "data": json.dumps({"error": f"推理出错: {str(e)}"}, ensure_ascii=False),
            }
        finally:
            tool_db.close()

    return EventSourceResponse(event_generator())
