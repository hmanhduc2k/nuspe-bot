import uuid

from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

DATABASE_URL = os.environ['DATABASE_URL1']

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

Base = declarative_base()

class Tasks(Base):
    __tablename__ = 'tasks'
    
    task_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id = Column(String)
    task_name = Column(String)
    task_assignee = Column(String, default='None')
    task_deadlines = Column(Date)
    task_remarks = Column(String, default='None')
    status = Column(String, default='ongoing')
        
Base.metadata.create_all(engine)