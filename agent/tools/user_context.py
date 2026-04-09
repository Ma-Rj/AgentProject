"""
用户上下文管理
使用 Python contextvars 在 Agent 执行期间传递当前用户信息
避免工具函数需要显式参数传递
"""
from contextvars import ContextVar

# 上下文变量定义
_current_user_id: ContextVar[int] = ContextVar("current_user_id", default=0)
_current_user_city: ContextVar[str] = ContextVar("current_user_city", default="")
_current_db_session = ContextVar("current_db_session", default=None)


def set_user_context(user_id: int, city: str, db_session=None):
    """在 Agent 执行前设置当前用户上下文"""
    _current_user_id.set(user_id)
    _current_user_city.set(city or "")
    if db_session is not None:
        _current_db_session.set(db_session)


def get_user_id_from_context() -> int:
    """工具函数中获取当前用户 ID"""
    return _current_user_id.get()


def get_user_city_from_context() -> str:
    """工具函数中获取当前用户城市"""
    return _current_user_city.get()


def get_db_session_from_context():
    """工具函数中获取数据库 Session"""
    return _current_db_session.get()
