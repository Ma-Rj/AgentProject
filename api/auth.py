"""
认证相关 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.database import get_db
from db import crud
from schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    UserInfoResponse,
)
from auth.password import hash_password, verify_password
from auth.jwt_handler import create_access_token, create_refresh_token, decode_token
from auth.dependencies import get_current_user
from db.models import User
from utils.logger_hander import logger

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(req: UserRegisterRequest, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查用户名是否已存在
    if crud.get_user_by_username(db, req.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="用户名已被注册",
        )

    # 检查邮箱是否已存在
    if crud.get_user_by_email(db, req.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="邮箱已被注册",
        )

    # 创建用户
    hashed_pwd = hash_password(req.password)
    user = crud.create_user(db, req.username, req.email, hashed_pwd, req.city)
    logger.info(f"[Auth] 用户注册成功: {req.username}")

    # 生成 Token
    access_token = create_access_token(user.id, user.username)
    refresh_token = create_refresh_token(user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/login", response_model=TokenResponse)
async def login(req: UserLoginRequest, db: Session = Depends(get_db)):
    """用户登录"""
    # 查找用户
    user = crud.get_user_by_username(db, req.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    # 验证密码
    if not verify_password(req.password, user.hashed_pwd):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    logger.info(f"[Auth] 用户登录成功: {req.username}")

    # 生成 Token
    access_token = create_access_token(user.id, user.username)
    refresh_token = create_refresh_token(user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(req: RefreshTokenRequest, db: Session = Depends(get_db)):
    """刷新 Access Token"""
    payload = decode_token(req.refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh Token 无效或已过期",
        )

    user_id = int(payload.get("sub", 0))
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
        )

    # 生成新的 Token 对
    access_token = create_access_token(user.id, user.username)
    new_refresh_token = create_refresh_token(user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
    )


@router.get("/me", response_model=UserInfoResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息"""
    return UserInfoResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        city=current_user.city,
        created_at=current_user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
    )
