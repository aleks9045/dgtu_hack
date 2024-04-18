from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP

from database import db_session
Base = db_session.base

from api.auth.models import UserModel


class ChatModel(Base):
    __tablename__ = "chat"
    chat_id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    user = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    time = Column(TIMESTAMP, nullable=False)
    message = Column(String(1024), nullable=False)
