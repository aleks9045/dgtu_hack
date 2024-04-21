from sqlalchemy import Column, SmallInteger, VARCHAR, ForeignKey

from database import db_session
Base = db_session.base

class TeamModel(Base):
    __tablename__ = "team"
    id_t = Column(SmallInteger, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(32), nullable=False, unique=True)
    about = Column(VARCHAR(255), nullable=True)
    banner = Column(VARCHAR(255), nullable=True)


class TeamLeadModel(Base):
    __tablename__ = "teamlead"
    id_tl = Column(SmallInteger, primary_key=True, autoincrement=True)
    user = Column(SmallInteger, ForeignKey('user.id_u', ondelete="CASCADE"), nullable=True)
    team = Column(SmallInteger, ForeignKey('team.id_t', ondelete="CASCADE"), nullable=True)


class JobModel(Base):
    __tablename__ = "job"
    id_j = Column(SmallInteger, primary_key=True, autoincrement=True)
    github = Column(VARCHAR(255), nullable=True)
    case = Column(SmallInteger, ForeignKey('case.id_ca', ondelete="CASCADE"), nullable=False)
    team = Column(SmallInteger, ForeignKey('team.id_t', ondelete="CASCADE"), nullable=False, unique=True)


class MarkModel(Base):
    __tablename__ = "job"
    id_m = Column(SmallInteger, primary_key=True, autoincrement=True)
    design = Column(SmallInteger, nullable=False)
    usability = Column(SmallInteger, nullable=False)
    backend = Column(SmallInteger, nullable=False)
    frontend = Column(SmallInteger, nullable=False)
    realization = Column(SmallInteger, nullable=False)
    comment = Column(VARCHAR(255), nullable=True)
    user = Column(SmallInteger, ForeignKey('user.id_u', ondelete="CASCADE"), nullable=False)
    expert = Column(SmallInteger, ForeignKey('expert.id_e', ondelete="CASCADE"), nullable=False)
    job = Column(SmallInteger, ForeignKey('jib.id_j', ondelete="CASCADE"), nullable=False)