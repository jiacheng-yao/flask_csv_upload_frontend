from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy_declarative import Base, CSVUpload_User

from werkzeug import generate_password_hash

engine = create_engine('sqlite:///csvupload_user.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

# Insert a new user in the CSVUploader_User table

_username = 'test'
_password = 'test'

_hashed_password = generate_password_hash(_password)

new_user = CSVUpload_User(username=_username, password=_hashed_password)
session.add(new_user)
session.commit()
