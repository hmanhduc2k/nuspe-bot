import uuid

from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP
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
    def __init__(self, chat_id, task_name, task_assignee, task_deadlines, task_remarks):
        self.task_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        self.chat_id = chat_id
        self.task_name = task_name
        self.task_assignee = task_assignee
        self.task_deadlines = task_deadlines
        self.task_remarks = task_remarks
        self.status = 'ongoing'
        
Base.metadata.create_all(engine)