from sqlalchemy import Column, Integer, String

from database import db_session
Base = db_session.base

class UserModel(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    # email = Column(String(32), nullable=False, unique=True)
    name = Column(String(32), nullable=False, unique=True)
    hashed_password = Column(String(1023), nullable=False)
    photo = Column(String(255), nullable=True)
