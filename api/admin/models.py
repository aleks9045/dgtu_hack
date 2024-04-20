from sqlalchemy import Column, SmallInteger, VARCHAR, ForeignKey, ForeignKeyConstraint

from database import db_session
Base = db_session.base


class AdminModel(Base):
    __tablename__ = "admin"
    id_a = Column(SmallInteger, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(32), nullable=False)
    hashed_password = Column(VARCHAR(1023), nullable=False)
