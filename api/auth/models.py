from sqlalchemy import Column, SmallInteger, VARCHAR, ForeignKey, ForeignKeyConstraint

from database import db_session
Base = db_session.base



class UserModel(Base):
    __tablename__ = "user"
    id_u = Column(SmallInteger, primary_key=True, autoincrement=True)
    first_name = Column(VARCHAR(32), nullable=False)
    last_name = Column(VARCHAR(32), nullable=False)
    father_name = Column(VARCHAR(32), nullable=True)
    email = Column(VARCHAR(64), nullable=False, unique=True)
    role = Column(VARCHAR(32), nullable=False)
    about = Column(VARCHAR(255), nullable=True)
    hashed_password = Column(VARCHAR(1023), nullable=False)
    photo = Column(VARCHAR(255), nullable=True)
    team = Column(SmallInteger, ForeignKey('team.id_t', ondelete="SET NULL"), nullable=True)