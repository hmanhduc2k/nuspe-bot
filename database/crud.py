import telebot
from telebot import types
from telebot_calendar import *
import telebot_calendar
import datetime
from datetime import timedelta
import schedule
import sched
import time
import os
import threading
import csv
import uuid
from collections import defaultdict
from database.model import Tasks, Event, Reminder
from database.database import Session
from sqlalchemy import cast, Date, extract
from sqlalchemy.sql.expression import and_, or_

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
        
def add_event(session, payload):
    try:
        event_date = payload['date']
        event_name = payload['name']
        chat_id = payload['chat_id']
        date_obj = datetime.datetime.strptime(event_date, "%d.%m.%Y")
        event = Event(
            chat_id=chat_id,
            event_name=event_name,
        )
        session.add(event)
        session.commit()
    except Exception as e:
        session.rollback()
        print('An error occurred', e)
        
def delete_task(session, task_id):
    try:
        target = session.query(Tasks).filter_by(task_id).first()
        if target:
            session.delete(target)
            session.commit()
            print('Task deleted')
    except Exception as e:
        session.rollback()
        
def show_task_by_date(session, chat_id, start_date, end_date):
    return session.query(Tasks).filter(
                and_(Tasks.chat_id == str(chat_id), Tasks.status =='ongoing')
            ).filter(
                and_(extract('day', Tasks.task_deadlines - start_date) >= 0, extract('day', Tasks.task_deadlines - end_date) <= 0)
            ).all()

def show_task_by_assignee(session, chat_id, assignee):
    return session.query(Tasks).filter_by(and_(Tasks.chat_id==str(chat_id), Tasks.assignee==assignee))
        