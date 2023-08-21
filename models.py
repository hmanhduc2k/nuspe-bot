import uuid

from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

DATABASE_URL = os.environ['DATABASE_URL1']

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

Base = declarative_base()

class Tasks:
    def __init__(self, chat_id, task_name, task_assignee, task_deadlines, task_remarks):
        self.task_id = uuid.uuid4()
        self.chat_id = chat_id
        self.task_name = task_name
        self.task_assignee = task_assignee
        self.task_deadlines = task_deadlines
        self.task_remarks = task_remarks
        self.status = 'ongoing'
        
Base.metadata.create_all(engine)