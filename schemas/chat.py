"""
聊天相关的 Pydantic 数据模型
"""
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """聊天请求"""
    message: str = Field(..., min_length=1, max_length=5000, description="用户消息内容")


class MessageResponse(BaseModel):
    """消息响应"""
    id: int
    role: str
    content: str
    created_at: str

    class Config:
        from_attributes = True
