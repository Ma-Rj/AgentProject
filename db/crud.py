"""
CRUD 操作封装
"""
import csv
from sqlalchemy.orm import Session
from db.models import User, Conversation, Message, DeviceRecord
from utils.logger_hander import logger


# ==================== User CRUD ====================

def create_user(db: Session, username: str, email: str, hashed_pwd: str, city: str = None) -> User:
    """创建用户"""
    user = User(username=username, email=email, hashed_pwd=hashed_pwd, city=city)
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info(f"[CRUD] 创建用户成功: {username}")
    return user


def get_user_by_username(db: Session, username: str) -> User | None:
    """根据用户名查询用户"""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    """根据邮箱查询用户"""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """根据ID查询用户"""
    return db.query(User).filter(User.id == user_id).first()


def update_user_city(db: Session, user_id: int, city: str) -> User | None:
    """更新用户城市"""
    user = get_user_by_id(db, user_id)
    if user:
        user.city = city
        db.commit()
        db.refresh(user)
    return user


# ==================== Conversation CRUD ====================

def create_conversation(db: Session, user_id: int, title: str = "新对话") -> Conversation:
    """创建对话"""
    conv = Conversation(user_id=user_id, title=title)
    db.add(conv)
    db.commit()
    db.refresh(conv)
    logger.info(f"[CRUD] 创建对话: user_id={user_id}, title={title}")
    return conv


def get_user_conversations(db: Session, user_id: int) -> list[Conversation]:
    """获取用户所有对话（按更新时间倒序）"""
    return (
        db.query(Conversation)
        .filter(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
        .all()
    )


def get_conversation_by_id(db: Session, conversation_id: int, user_id: int) -> Conversation | None:
    """获取指定对话（需验证用户归属）"""
    return (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id, Conversation.user_id == user_id)
        .first()
    )


def update_conversation_title(db: Session, conversation_id: int, user_id: int, title: str) -> Conversation | None:
    """更新对话标题"""
    conv = get_conversation_by_id(db, conversation_id, user_id)
    if conv:
        conv.title = title
        db.commit()
        db.refresh(conv)
    return conv


def delete_conversation(db: Session, conversation_id: int, user_id: int) -> bool:
    """删除对话（级联删除所有消息）"""
    conv = get_conversation_by_id(db, conversation_id, user_id)
    if conv:
        db.delete(conv)
        db.commit()
        logger.info(f"[CRUD] 删除对话: conversation_id={conversation_id}")
        return True
    return False


# ==================== Message CRUD ====================

def add_message(db: Session, conversation_id: int, role: str, content: str) -> Message:
    """添加消息"""
    msg = Message(conversation_id=conversation_id, role=role, content=content)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def get_conversation_messages(db: Session, conversation_id: int) -> list[Message]:
    """获取对话的所有消息（按时间排序）"""
    return (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .all()
    )


# ==================== DeviceRecord CRUD ====================

def get_device_record(db: Session, user_id: int, month: str) -> DeviceRecord | None:
    """获取指定用户在指定月份的设备使用记录"""
    return (
        db.query(DeviceRecord)
        .filter(DeviceRecord.user_id == user_id, DeviceRecord.month == month)
        .first()
    )


def import_csv_to_db(db: Session, csv_path: str):
    """
    将 records.csv 数据批量导入到 device_records 表
    注意：CSV 中的 user_id 是字符串如 "1001"，需要先确保对应用户已存在
    此函数会先创建占位用户（如果不存在），然后导入记录
    """
    existing_count = db.query(DeviceRecord).count()
    if existing_count > 0:
        logger.info(f"[CSV导入] device_records 表已有 {existing_count} 条记录，跳过导入")
        return

    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)  # 跳过表头
            records = []
            for row in reader:
                if len(row) < 6:
                    continue
                user_id_str = row[0].strip().strip('"')
                feature = row[1].strip().strip('"')
                efficiency = row[2].strip().strip('"')
                consumables = row[3].strip().strip('"')
                comparison = row[4].strip().strip('"')
                month = row[5].strip().strip('"')

                # 确保用户存在（创建占位用户）
                user_id_int = int(user_id_str)
                existing_user = get_user_by_id(db, user_id_int)
                if not existing_user:
                    placeholder_user = User(
                        id=user_id_int,
                        username=f"user_{user_id_str}",
                        email=f"user_{user_id_str}@placeholder.com",
                        hashed_pwd="placeholder_not_for_login",
                        city=None,
                    )
                    db.add(placeholder_user)
                    db.flush()

                records.append(DeviceRecord(
                    user_id=user_id_int,
                    feature=feature,
                    efficiency=efficiency,
                    consumables=consumables,
                    comparison=comparison,
                    month=month,
                ))

            db.bulk_save_objects(records)
            db.commit()
            logger.info(f"[CSV导入] 成功导入 {len(records)} 条设备使用记录到数据库")

    except Exception as e:
        db.rollback()
        logger.error(f"[CSV导入] 导入失败: {str(e)}", exc_info=True)
        raise
