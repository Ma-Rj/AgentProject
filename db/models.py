"""
ORM 模型定义
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    email = Column(String(100), unique=True, nullable=False, index=True, comment="邮箱")
    hashed_pwd = Column(String(255), nullable=False, comment="哈希密码")
    city = Column(String(50), nullable=True, default=None, comment="用户所在城市")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    # 关联关系
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    device_records = relationship("DeviceRecord", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"


class Conversation(Base):
    """对话表"""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), default="新对话", comment="对话标题")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关联关系
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan",
                            order_by="Message.created_at")

    def __repr__(self):
        return f"<Conversation(id={self.id}, title={self.title})>"


class Message(Base):
    """消息表"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(Enum("user", "assistant", "system", "tool", name="message_role"), nullable=False, comment="消息角色")
    content = Column(Text, nullable=False, comment="消息内容")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    # 关联关系
    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, role={self.role})>"


class DeviceRecord(Base):
    """设备使用记录表（由 CSV 迁移而来）"""
    __tablename__ = "device_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    feature = Column(Text, nullable=False, comment="用户特征（户型、地面类型等）")
    efficiency = Column(Text, nullable=False, comment="清洁效率数据")
    consumables = Column(Text, nullable=False, comment="耗材状态")
    comparison = Column(Text, nullable=False, comment="使用对比")
    month = Column(String(7), nullable=False, comment="记录月份 YYYY-MM")

    # 复合索引：按用户ID和月份快速查询
    __table_args__ = (
        Index("idx_user_month", "user_id", "month"),
    )

    # 关联关系
    user = relationship("User", back_populates="device_records")

    def __repr__(self):
        return f"<DeviceRecord(user_id={self.user_id}, month={self.month})>"
