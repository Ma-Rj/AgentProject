"""
对话管理 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.database import get_db
from db import crud
from db.models import User
from schemas.conversation import ConversationCreateRequest, ConversationUpdateRequest, ConversationResponse
from schemas.chat import MessageResponse
from auth.dependencies import get_current_user
from utils.logger_hander import logger

router = APIRouter(prefix="/api/conversations", tags=["对话管理"])


@router.get("", response_model=list[ConversationResponse])
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前用户的所有对话"""
    conversations = crud.get_user_conversations(db, current_user.id)
    return [
        ConversationResponse(
            id=conv.id,
            title=conv.title,
            created_at=conv.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            updated_at=conv.updated_at.strftime("%Y-%m-%d %H:%M:%S") if conv.updated_at else "",
        )
        for conv in conversations
    ]


@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    req: ConversationCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建新对话"""
    conv = crud.create_conversation(db, current_user.id, req.title)
    return ConversationResponse(
        id=conv.id,
        title=conv.title,
        created_at=conv.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        updated_at=conv.updated_at.strftime("%Y-%m-%d %H:%M:%S") if conv.updated_at else "",
    )


@router.patch("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: int,
    req: ConversationUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新对话标题"""
    conv = crud.update_conversation_title(db, conversation_id, current_user.id, req.title)
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="对话不存在")
    return ConversationResponse(
        id=conv.id,
        title=conv.title,
        created_at=conv.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        updated_at=conv.updated_at.strftime("%Y-%m-%d %H:%M:%S") if conv.updated_at else "",
    )


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除对话及其所有消息"""
    success = crud.delete_conversation(db, conversation_id, current_user.id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="对话不存在")


@router.get("/{conversation_id}/messages", response_model=list[MessageResponse])
async def get_messages(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取对话的所有消息"""
    # 验证对话归属
    conv = crud.get_conversation_by_id(db, conversation_id, current_user.id)
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="对话不存在")

    messages = crud.get_conversation_messages(db, conversation_id)
    return [
        MessageResponse(
            id=msg.id,
            role=msg.role,
            content=msg.content,
            created_at=msg.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        )
        for msg in messages
    ]
