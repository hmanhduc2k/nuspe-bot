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
from models import Tasks
from models import Session
from sqlalchemy import cast, Date, extract
from sqlalchemy.sql.expression import and_, or_


calendar = Calendar(language=ENGLISH_LANGUAGE)
calendar_1 = CallbackData('calendar_1', 'action', 'year', 'month', 'day')

def reply_to_add_task(bot, message):
    now = datetime.datetime.now()
    bot.send_message(message.chat.id, 'Which date do you want to add a task to?', 
            reply_markup=calendar.create_calendar(
                name=calendar_1.prefix,
                year=now.year,
                month=now.month)
            )
    
def attach(bot_instance):
    @bot_instance.message_handler(commands=['add_task'])
    def add_tasks(message):
        # return add_task_module(message, bot)
        reply_to_add_task(bot_instance, message)
        
def attach_callback(bot_instance):
    @bot_instance.callback_query_handler(func=lambda call: call.data.startswith(calendar_1.prefix))
    def callback_addtask(call: types.CallbackQuery):
        name, action, year, month, day = call.data.split(calendar_1.sep)
        date = calendar.calendar_query_handler(bot=bot_instance, call=call, name=name, action=action, year=year, month=month, day=day)
        if action == 'DAY':
            c_date = date.strftime("%d.%m.%Y")
            msg = bot_instance.send_message(chat_id=call.message.chat.id, text=f'You chose {c_date}, please enter your plan.\nFormat your plan this way: task_name|assignee|remarks: ')
            bot_instance.register_next_step_handler(msg, lambda message: add_task_module(message, chat_id=call.message.chat.id, c_date=c_date))
        elif action == 'CANCEL':
            bot_instance.send_message(chat_id=call.message.chat.id, text='🚫 Cancelled')
        
        
# # the function of adding a new task
# def add_task_module(session, message, chat_id, c_date):
#     try:
#         add_todo(chat_id, c_date, message)
#         text = f'Task successfully registered on {c_date}'
#         bot.send_message(chat_id=chat_id, text=text)
#     except:
#         bot.send_message(chat_id=chat_id, text='Error occurred! Please format your plan this way: \n[task name]|[assignee]|[remarks]\nLeave blank but keep the | if do not have')
        

# # the function adds a task to the todos dictionary
# def add_todo(chat_id, c_date, message):
#     task, assignee, remarks = message.text.split('|')
#     print(c_date)
#     date_obj = datetime.datetime.strptime(c_date, "%d.%m.%Y")
#     obj = Tasks(
#         chat_id=chat_id, 
#         task_name=task, 
#         task_assignee=assignee, 
#         task_deadlines=date_obj, 
#         task_remarks=remarks
#     )
#     session.add(obj)
#     session.commit()