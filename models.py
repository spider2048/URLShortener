import datetime
from sqlalchemy import Column, Integer, String, Text, Time
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class URLTable(Base):
    __tablename__ = "URLHashMapping"

    id = Column(Integer, primary_key=True, autoincrement=True)
    hash = Column(String(6))
    url = Column(Text())

class URLStats(Base):
    __tablename__  = "UrlStats"
    id: Column[int] = Column(Integer, primary_key=True, autoincrement=True)
    hash: Column[str] = Column(String(6))
    times: Column[int] = Column(Integer)

class URLRefs(Base):
    __tablename__ = "UrlRefererTable"

    id: Column[int] = Column(Integer, primary_key=True, autoincrement=True)
    hash: Column[str] = Column(String(6))
    referer: Column[str] = Column(Text())
    ip: Column[str] = Column(Text())
    time = Column(Text())

    def __repr__(self) -> str:
        return repr(dict(
            id=self.id,
            hash=self.hash,
            referer=self.referer,
            ip=self.ip,
            time=self.time
        ))