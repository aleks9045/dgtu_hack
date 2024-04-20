from sqlalchemy import Column, SmallInteger, VARCHAR, ForeignKey

from database import db_session
Base = db_session.base

class ExpertModel(Base):
    __tablename__ = "expert"
    id_e = Column(SmallInteger, primary_key=True, autoincrement=True)
    first_name = Column(VARCHAR(32), nullable=False)
    last_name = Column(VARCHAR(32), nullable=False)
    father_name = Column(VARCHAR(32), nullable=True)
    email = Column(VARCHAR(64), nullable=False, unique=True)
    role = Column(VARCHAR(32), nullable=False)
    hashed_password = Column(VARCHAR(1023), nullable=False)
    photo = Column(VARCHAR(255), nullable=True)
    company = Column(SmallInteger, ForeignKey('company.id_co'), nullable=False)



class MarkModel(Base):
    __tablename__ = "mark"
    id_m = Column(SmallInteger, primary_key=True, autoincrement=True)
    design = Column(VARCHAR(32), nullable=True)
    usability = Column(VARCHAR(32), nullable=True)
    backend = Column(VARCHAR(32), nullable=True)
    frontend = Column(VARCHAR(32), nullable=True)
    realization = Column(VARCHAR(32), nullable=True)
    comment = Column(VARCHAR(255), nullable=True)
    job = Column(SmallInteger, ForeignKey('job.id_j', ondelete="CASCADE"), nullable=True)
    expert = Column(SmallInteger, ForeignKey('expert.id_e', ondelete="CASCADE"), nullable=True)
    user = Column(SmallInteger, ForeignKey('user.id_u', ondelete="CASCADE"), nullable=True)

class CaseModel(Base):
    __tablename__ = "case"
    id_ca = Column(SmallInteger, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(64), nullable=False, unique=True)
    about = Column(VARCHAR(255), nullable=True)
    file = Column(VARCHAR(255), nullable=False)
    company = Column(SmallInteger, ForeignKey('company.id_co', ondelete="CASCADE"), nullable=True)

class CompanyModel(Base):
    __tablename__ = "company"
    id_co = Column(SmallInteger, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(32), nullable=False)

