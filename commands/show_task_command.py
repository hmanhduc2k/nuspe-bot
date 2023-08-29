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
from database.model import Tasks
from database.database import Session
from sqlalchemy import cast, Date, extract
from sqlalchemy.sql.expression import and_, or_
from database import crud

calendar = Calendar(language=ENGLISH_LANGUAGE)
calendar_2 = CallbackData('calendar_2', 'action', 'year', 'month', 'day')
calendar_3 = CallbackData('calendar_3', 'action', 'year', 'month', 'day')

def attach_show(bot_instance):
    @bot_instance.message_handler(commands=['show_task'])
    def show_task(message):
        test_show_task(bot_instance, message)
        
def attach_show_callback_1(bot_instance):
    @bot_instance.callback_query_handler(func=lambda call: call.data.startswith(calendar_2.prefix))
    def callback_1(call: types.CallbackQuery):
        now = datetime.datetime.now()
        name, action, year, month, day = call.data.split(calendar_2.sep)
        date = calendar.calendar_query_handler(bot=bot_instance, call=call, name=name, action=action, year=year, month=month, day=day)
        if action == 'DAY':
            c_date = date.strftime("%d.%m.%Y")
            bot_instance.send_message(
                call.message.chat.id, f'Show events starting from: {c_date}. Select an end date:', 
                reply_markup=calendar.create_calendar(
                    name=calendar_3.prefix,
                    year=now.year,
                    month=now.month)
            )
        elif action == 'CANCEL':
            bot_instance.send_message(chat_id=call.message.chat.id, text='🚫 Cancelled')

def attach_show_callback_2(bot_instance):
    @bot_instance.callback_query_handler(func=lambda call: call.data.startswith(calendar_3.prefix))
    def callback_2(call: types.CallbackQuery):
        print(call.message.text)
        start_date = call.message.text.split('. ')[0].split(': ')[1]
        name, action, year, month, day = call.data.split(calendar_3.sep)
        date = calendar.calendar_query_handler(bot=bot_instance, call=call, name=name, action=action, year=year, month=month, day=day)
        if action == 'DAY':
            start_date = datetime.datetime.strptime(start_date, "%d.%m.%Y")
            end_date = date.strftime("%d.%m.%Y")
            end_date = datetime.datetime.strptime(end_date, "%d.%m.%Y")
            filtered = crud.show_task_by_date(chat_id=call.message.chat.id, start_date=start_date, end_date=end_date)
            if filtered == []:
                bot_instance.send_message(call.message.chat.id, 'No task is available now')
            bot_instance.send_message(
                call.message.chat.id, f'Show events starting from: {start_date.date()} to {end_date.date()}', 
            )

            dates = defaultdict(list)
            for value in filtered:
                date = value.task_deadlines
                print(date)
                dates[date].append(value)
                
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            for date, tasks in dates.items():
                for task in tasks:
                    temp = task.task_deadlines.date()
                    button = types.InlineKeyboardButton(text=f'Due {temp}: {task.task_name}', callback_data=f"select@@{task.task_id}")
                    keyboard.add(button)
            bot_instance.send_message(call.message.chat.id, 'List', reply_markup=keyboard)
        elif action == 'CANCEL':
            bot_instance.send_message(chat_id=call.message.chat.id, text='🚫 Cancelled')


def test_show_task(bot, message):
    now = datetime.datetime.now()
    bot.send_message(message.chat.id, 'Select start date', 
            reply_markup=calendar.create_calendar(
                name=calendar_2.prefix,
                year=now.year,
                month=now.month)
            )
    
# @bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_2.prefix))
# def callback_1(call: types.CallbackQuery):
#     name, action, year, month, day = call.data.split(calendar_2.sep)
#     date = calendar.calendar_query_handler(bot=bot, call=call, name=name, action=action, year=year, month=month, day=day)
#     if action == 'DAY':
#         c_date = date.strftime("%d.%m.%Y")
#         bot.send_message(
#             call.message.chat.id, f'Show events starting from: {c_date}. Select an end date:', 
#             reply_markup=calendar.create_calendar(
#                 name=calendar_3.prefix,
#                 year=now.year,
#                 month=now.month)
#         )
#         # bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='Clicked')
#         # bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.id, text='Clicked')
        
# @bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_3.prefix))
# def callback_2(call: types.CallbackQuery):
#     print(call.message.text)
#     start_date = call.message.text.split('. ')[0].split(': ')[1]
#     name, action, year, month, day = call.data.split(calendar_1.sep)
#     date = calendar.calendar_query_handler(bot=bot, call=call, name=name, action=action, year=year, month=month, day=day)
#     if action == 'DAY':
#         start_date = datetime.datetime.strptime(start_date, "%d.%m.%Y")
#         end_date = date.strftime("%d.%m.%Y")
#         end_date = datetime.datetime.strptime(end_date, "%d.%m.%Y")
#         filtered = session.query(Tasks).filter(
#                 and_(Tasks.chat_id == str(call.message.chat.id), Tasks.status =='ongoing')
#             ).filter(
#                 and_(extract('day', Tasks.task_deadlines - start_date) >= 0, extract('day', Tasks.task_deadlines - end_date) <= 0)
#             ).all()
#         if filtered == []:
#             bot.send_message(call.message.chat.id, 'No task is available now')
#         bot.send_message(
#             call.message.chat.id, f'Show events starting from: {start_date.date()} to {end_date.date()}', 
#         )

#         dates = defaultdict(list)
#         for value in filtered:
#             date = value.task_deadlines
#             print(date)
#             dates[date].append(value)
            
#         keyboard = types.InlineKeyboardMarkup(row_width=2)
#         for date, tasks in dates.items():
#             for task in tasks:
#                 temp = task.task_deadlines.date()
#                 button = types.InlineKeyboardButton(text=f'Due {temp}: {task.task_name}', callback_data=f"select@@{task.task_id}")
#                 keyboard.add(button)
#         bot.send_message(call.message.chat.id, 'List', reply_markup=keyboard)


# @bot.message_handler(commands=['show_task'])
# def show_tasks(message):
#     print(message)
#     print(message.text.split(' '))
#     filtered = session.query(Tasks).filter_by(chat_id=str(message.chat.id), status='ongoing').all()
#     print('Show tasks called', message.chat.id)
                
#     if filtered == []:
#         bot.send_message(message.chat.id, 'No task is available now')

#     dates = defaultdict(list)
#     for value in filtered:
#         date = value.task_deadlines
#         dates[date].append(value)
        
#     print(dates)
        
#     for date, tasks in dates.items():
#         tasks_text = '\n'.join(f'- {task.task_name} assigned to {task.task_assignee}' for task in tasks)
#         text = f'Tasks for {date}:'
#         keyboard = types.InlineKeyboardMarkup(row_width=1)
#         for task in tasks:
#             # button = types.InlineKeyboardButton(text=f'View: {task.task_name}', callback_data=f'delete@@{task.task_name}@@{task.task_deadlines}')
#             button = types.InlineKeyboardButton(text=f'View: {task.task_name}', callback_data=f"select@@{task.task_id}")
#             keyboard.add(button)
#         bot.send_message(message.chat.id, text, reply_markup=keyboard)