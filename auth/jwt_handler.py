"""
JWT Token 生成与验证
"""
import os
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError, ExpiredSignatureError
from dotenv import load_dotenv
from utils.logger_hander import logger

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "default-secret-key-change-me")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))


def create_access_token(user_id: int, username: str) -> str:
    """
    创建访问 Token (短期)
    :param user_id: 用户 ID
    :param username: 用户名
    :return: JWT 字符串
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "username": username,
        "exp": expire,
        "type": "access",
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(user_id: int) -> str:
    """
    创建刷新 Token (长期)
    :param user_id: 用户 ID
    :return: JWT 字符串
    """
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh",
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict | None:
    """
    解码并验证 Token
    :param token: JWT 字符串
    :return: payload 字典，验证失败返回 None
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        logger.warning("[JWT] Token 已过期")
        return None
    except JWTError as e:
        logger.warning(f"[JWT] Token 验证失败: {str(e)}")
        return None
