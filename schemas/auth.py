"""
认证相关的 Pydantic 数据模型
"""
from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """用户注册请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: str = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    city: str | None = Field(None, max_length=50, description="所在城市")


class UserLoginRequest(BaseModel):
    """用户登录请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class TokenResponse(BaseModel):
    """Token 响应"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """刷新 Token 请求"""
    refresh_token: str


class UserInfoResponse(BaseModel):
    """用户信息响应"""
    id: int
    username: str
    email: str
    city: str | None
    created_at: str

    class Config:
        from_attributes = True
