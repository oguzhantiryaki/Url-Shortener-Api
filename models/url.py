from sqlalchemy import DateTime,Column,Integer,String
from config.db import Base
from datetime import datetime


class Url(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    orginalUrl = Column(String(255))
    shortUrl = Column(String(50), unique=True)
    createDate = Column(DateTime,default=datetime.now())

class UrlLog(Base):
    __tablename__ = "urllogs"
    id = Column(Integer, primary_key=True, index=True)
    shortUrl = Column(String(50))
    accessDate = Column(DateTime,default=datetime.now())
    