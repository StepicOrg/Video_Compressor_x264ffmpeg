from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from settings import URL_GET_FILE_PAGE_PATH, URL_GET_DIRECT_FILE_PATH
import os.path

Base = declarative_base()

def insert_to_db(md5_name, file_name):
    new_file = MainDatabase(md5_name=md5_name, real_name=file_name,
                           token=os.path.splitext(md5_name)[0])
    session.add(new_file)
    session.commit()
    return new_file


class MainDatabase(Base):
    __tablename__ = 'files'

    id = Column(Integer, primary_key=True)
    md5_name = Column(String(250), nullable=False)
    real_name = Column(String)
    token = Column(String, nullable=False)
    finished = Column(Boolean, default=False)

    @property
    def url(self):
        fileName, _ = os.path.splitext(self.md5_name)
        return "/" + URL_GET_FILE_PAGE_PATH + "/" + fileName

    @property
    def file_url(self):
        return "/" + URL_GET_DIRECT_FILE_PATH + "/" + self.md5_name


class FileLookupByToken(object):
    def __init__(self, token):
        self.db_obj = session.query(MainDatabase).filter(MainDatabase.token == token)
        # if self.db_obj.count() != 1:
        #     raise IndexError
        # else:
        self.db_obj = self.db_obj[0]

    def file_url(self):
        return "/" + URL_GET_DIRECT_FILE_PATH + "/" + self.db_obj.md5_name

engine = create_engine('sqlite:///compressor.db')

dbpath = os.path.join(os.path.dirname(__file__), "compressor.db")
if not os.path.isfile(dbpath):
    Base.metadata.create_all(engine)

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()