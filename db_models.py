from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from settings import URL_GET_FILE_PATH

Base = declarative_base()

class FileLookup(Base):
    __tablename__ = 'files'

    id = Column(Integer, primary_key=True)
    md5_name = Column(String(250), nullable=False)
    real_name = Column(String)

    @property
    def url(self):
        return URL_GET_FILE_PATH + "/" + self.md5_name


engine = create_engine('sqlite:///compressor.db')


Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
