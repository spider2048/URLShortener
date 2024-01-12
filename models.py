from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class URLTable(Base):
    __tablename__ = "URLHashMapping"

    id = Column(Integer, primary_key=True, autoincrement=True)
    hash = Column(String(6))
    url = Column(Text())
