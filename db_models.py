import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class FileLookup(Base):
    __tablename__ = 'files'

    id = Column(Integer, primary_key=True)
    md5_name = Column(String(250), nullable=False)
    real_name = Column(String)


engine = create_engine('sqlite:///compressor.db')


Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
