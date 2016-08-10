from sqlalchemy_declarative import CSVUpload_User, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///csvupload_user.db')
Base.metadata.bind = engine

DBSession = sessionmaker()
DBSession.bind = engine
session = DBSession()

user = session.query(CSVUpload_User).first()

print user.password