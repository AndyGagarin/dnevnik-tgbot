from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, BigInteger, String

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    tg_user_id = Column(BigInteger, unique=True, index=True, nullable=False)
    token = Column(String(500), nullable=False)

