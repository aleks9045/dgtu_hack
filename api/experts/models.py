from sqlalchemy import Column, SmallInteger, VARCHAR, ForeignKey

from database import db_session
Base = db_session.base


class CaseModel(Base):
    __tablename__ = "case"
    id_c = Column(SmallInteger, primary_key=True, autoincrement=True)
    case = Column(SmallInteger, ForeignKey(''), nullable=False)
