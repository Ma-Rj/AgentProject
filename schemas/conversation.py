"""
对话管理相关的 Pydantic 数据模型
"""
from pydantic import BaseModel, Field


class ConversationCreateRequest(BaseModel):
    """创建对话请求"""
    title: str = Field(default="新对话", max_length=200, description="对话标题")


class ConversationUpdateRequest(BaseModel):
    """更新对话请求"""
    title: str = Field(..., max_length=200, description="新标题")


class ConversationResponse(BaseModel):
    """对话响应"""
    id: int
    title: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
