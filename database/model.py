import uuid

from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP, Date, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Tasks(Base):
    __tablename__ = 'tasks'
    
    task_id = Column(UUID(as_uuid=True), primary_key=True, default=str(uuid.uuid4))
    event_id = Column(String, ForeignKey('reminders.reminder_id'), default=None)
    chat_id = Column(String)
    task_name = Column(String, nullable=False)
    task_assignee = Column(String, default='None')
    task_deadlines = Column(DateTime, nullable=False)
    task_remarks = Column(String, default='None')
    status = Column(String, default='ongoing')
    
class Reminder(Base):
    __tablename__ = 'reminders'
    
    reminder_id = Column(UUID(as_uuid=True), primary_key=True, default=str(uuid.uuid4))
    task_id = Column(String, ForeignKey('tasks.task_id'), default=None)
    reminder_time = Column(DateTime)
    
class Event(Base):
    __tablename__ = 'events'
    
    event_id = Column(UUID(as_uuid=True), primary_key=True, default=str(uuid.uuid4))
    event_name = Column(String)