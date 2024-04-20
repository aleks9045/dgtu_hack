from sqlalchemy import Column, String, ForeignKey, TIMESTAMP, SmallInteger

from database import db_session
Base = db_session.base

from api.auth.models import UserModel


class ChatModel(Base):
    __tablename__ = "chat"
    chat_id = Column(SmallInteger, primary_key=True, autoincrement=True, unique=True)
    user = Column(SmallInteger, ForeignKey("user.id_u", ondelete="CASCADE"), nullable=False)
    time = Column(TIMESTAMP, nullable=False)
    message = Column(String(1024), nullable=False)
