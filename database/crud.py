import uuid

from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP, Date, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from database.model import Base
from database.model import Tasks, Event, Reminder
import datetime

def add_task(session, payload):
    try:
        message = payload['message']
        task, assignee, remarks = message.text.split('|')
        taskdate = payload['date']
        chat_id = payload['chat_id']
        date_obj = datetime.datetime.strptime(taskdate, "%d.%m.%Y")
        obj = Tasks(
            chat_id=chat_id, 
            task_name=task, 
            task_assignee=assignee, 
            task_deadlines=date_obj, 
            task_remarks=remarks
        )
        session.add(obj)
        session.commit()
        return obj
    except Exception as e:
        session.rollback()
        print('An error occurred: ', e)
        
def delete_task(session, task_id):
    try:
        target = session.query(Tasks).filter_by(task_id).first()
        if target:
            session.delete(target)
            session.commit()
            print('Task deleted')
    except Exception as e:
        session.rollback()
        
def show_task_by_date():
    pass

def show_task_by_assignee():
    pass
        