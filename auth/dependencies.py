"""
FastAPI 依赖注入：认证相关
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from auth.jwt_handler import decode_token
from db.database import get_db
from db.crud import get_user_by_id
from db.models import User

# Bearer Token 认证方案
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    从请求 Header 中提取 JWT Token，验证并返回当前用户
    用法: 在路由函数参数中添加 current_user: User = Depends(get_current_user)
    """
    token = credentials.credentials

    # 解码 Token
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 无效或已过期，请重新登录",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 检查 Token 类型
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 类型错误，请使用 access_token",
        )

    # 获取用户
    user_id = int(payload.get("sub", 0))
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
        )

    return user
