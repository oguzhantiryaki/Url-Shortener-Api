from sqlalchemy import Table,Column,Integer,String,DateTime
from config.db import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(30), unique=True)
    email = Column(String(50), unique=True)
    password = Column(String(60), unique=True)
    lastUrlCreateDate=Column(DateTime, default=datetime.now().date)
    dailyCreatedUrl=Column(Integer,default=0)
