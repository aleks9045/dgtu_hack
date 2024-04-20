from sqlalchemy import Column, SmallInteger, VARCHAR, ForeignKey

from database import db_session
Base = db_session.base

class InviteModel(Base):
    __tablename__ = "invited"
    id_i = Column(SmallInteger, primary_key=True, autoincrement=True)
    user = Column(SmallInteger, ForeignKey('user.id_u', ondelete="CASCADE"), nullable=True)
    team = Column(SmallInteger, ForeignKey('team.id_t', ondelete="CASCADE"), nullable=True)
