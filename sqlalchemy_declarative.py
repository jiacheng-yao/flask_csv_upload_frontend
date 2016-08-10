import os
import sys
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

Base = declarative_base()


class CSVUpload_User(Base):
    __tablename__ = 'csvupload_user'
    id = Column(Integer, primary_key=True)
    username = Column(String(250), nullable=False)
    password = Column(String(250), nullable=False)


# Create an engine that stores data in the local directory's
# csvupload_user.db file.
engine = create_engine('sqlite:///csvupload_user.db')

# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)