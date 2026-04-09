"""
密码哈希与验证工具
使用 bcrypt 进行安全的密码哈希
"""
import bcrypt


def hash_password(plain_password: str) -> str:
    """
    对明文密码进行 bcrypt 哈希
    :param plain_password: 明文密码
    :return: 哈希后的密码字符串
    """
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证明文密码与哈希密码是否匹配
    :param plain_password: 明文密码
    :param hashed_password: 存储的哈希密码
    :return: 是否匹配
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )
