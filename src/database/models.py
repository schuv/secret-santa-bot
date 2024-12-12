from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    BigInteger
)


class Base(DeclarativeBase):
    pass


class UserModel(Base):
    __tablename__ = "users"

    id: int = Column("id", Integer, primary_key=True, unique=True)
    user_id: int = Column("user_id", BigInteger)
    username: str = Column("username", String)
    first_name: str = Column("first_name", String)
    last_name: str = Column("last_name", String)
    preferences: str = Column("preferences", String)
    verified: bool = Column("verified", Boolean)
    user_for_gift_id: int = Column("user_for_gift_id", Integer)
    gift_delivered: bool = Column("gift_delivered", Boolean, default=False)
    timestamp: int = Column("timestamp", BigInteger)
