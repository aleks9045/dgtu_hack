from sqlalchemy import Column, SmallInteger, VARCHAR, ForeignKey

from database import db_session
Base = db_session.base

class TeamModel(Base):
    __tablename__ = "team"
    id_t = Column(SmallInteger, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(32), nullable=False, unique=True)
    banner = Column(VARCHAR(64), nullable=True)
    job = Column(SmallInteger, ForeignKey('job.id_j'), nullable=True)
    about = Column(VARCHAR(255), nullable=True)


class TeamLeadModel(Base):
    __tablename__ = "teamlead"
    id_tl = Column(SmallInteger, primary_key=True, autoincrement=True)
    user = Column(SmallInteger, ForeignKey('user.id_u', ondelete="CASCADE"), nullable=True)
    team = Column(SmallInteger, ForeignKey('team.id_t', ondelete="CASCADE"), nullable=True)

class JobModel(Base):
    __tablename__ = "job"
    id_j = Column(SmallInteger, primary_key=True, autoincrement=True)
    # case = Column(SmallInteger, ForeignKey(''), nullable=False)