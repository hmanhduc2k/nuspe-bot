import uuid

from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP, Date, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

DATABASE_URL = os.environ['DATABASE_URL1']

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

Base = declarative_base()

Base.metadata.create_all(engine)