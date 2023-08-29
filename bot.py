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

from commands import add_task_module, start_module, help_module, add_tasks_command, show_task_command

session = Session()

TOKEN = '6177637545:AAH-qY4PytR-CGyCrG_OvpTrckaHpZ5Kv68'
bot = telebot.TeleBot(TOKEN)
calendar = Calendar(language=ENGLISH_LANGUAGE)
calendar_2 = CallbackData('calendar_2', 'action', 'year', 'month', 'day')
calendar_3 = CallbackData('calendar_3', 'action', 'year', 'month', 'day')

now = datetime.datetime.now()

reminder_started = False

add_task_module.attach(bot)
start_module.attach(bot)
help_module.attach(bot)
add_tasks_command.attach(bot)
add_tasks_command.attach_callback(bot)
show_task_command.attach_show(bot)
show_task_command.attach_show_callback_1(bot)
show_task_command.attach_show_callback_2(bot)

@bot.callback_query_handler(func=lambda call: call.data.startswith('select@@'))
def view_task(call):
    task_id = call.data.split('@@')[1]
    task = session.query(Tasks).filter_by(task_id=task_id).one_or_none()
    if task:
        view_button = types.InlineKeyboardButton(text=f'Edit task', callback_data=f'edit@@{task.task_id}')
        delete_button = types.InlineKeyboardButton(text=f'Delete task', callback_data=f'delete@@{task.task_id}')
        cancel_button = types.InlineKeyboardButton(text=f'Cancel', callback_data='cancel')
        
        keyboard = types.InlineKeyboardMarkup(
            [
                [view_button, delete_button], [cancel_button]
            ]
        )
        bot.send_message(call.message.chat.id, f'View {task.task_name}', reply_markup=keyboard)
        
        
@bot.callback_query_handler(func=lambda call: call.data.startswith('edit@@'))
def edit_task(call):
    task_id = call.data.split('@@')[1]
    edit_name = types.InlineKeyboardButton(text=f'Edit task', callback_data=f'editname@@{task_id}')
    edit_assignee = types.InlineKeyboardButton(text=f'Delete task', callback_data=f'editassignee@@{task_id}')
    edit_remarks = types.InlineKeyboardButton(text=f'Cancel', callback_data='editremark@@{task_id}')
    keyboard = types.InlineKeyboardMarkup(
            [
                [edit_name, edit_assignee, edit_remarks]
            ]
        )
    bot.send_message(call.message.chat.id, 'Select a field you want to edit', reply_markup=keyboard)

# task deletion function
def delete_task(chat_id, c_date, task):
    print(c_date)
    target = session.query(Tasks).filter_by(chat_id=str(chat_id), task_deadlines=c_date, task_name=task).first()
    if target:
        session.delete(target)
        session.commit()
        print('Task deleted')
        

# deletes the task and displays a message about the successful deletion of this task.
@bot.callback_query_handler(func=lambda call: call.data.startswith('delete@@'))
def delete_callback(call):
    print(call.data.split('@@'))
    _, task, date = call.data.split('@@')
    delete_task(call.message.chat.id, date, task)
    bot.answer_callback_query(call.id, text=f'Task "{task}" on {date} deleted. \nPlease restart by typing /show_task again')


# Define the function to send a reminder message
def send_reminder(chat_id):
    '''
    For all chat ids, retrieve all tasks available
    '''
    while True:
        print('System is run again')
        target = session.query(Tasks).filter_by(chat_id=str(chat_id)).all()
        
        now = datetime.datetime.now()
        for task in target:
            time_diff = task.task_deadlines - now
            hours = time_diff.total_seconds() // 3600
            if hours in [1, 6, 12, 24, 48, 72, 24 * 7]:
                reminder_text = f"Reminder for {task.task_name} assigned to {task.task_assignee}: \nYour task is approaching on {cast(task.task_deadlines, Date)}, and now is {now.date()}!"
                bot.send_message(chat_id=chat_id, text=reminder_text)
        
        time.sleep(3600)  # Wait for 1 hour

# Start a new thread for sending reminders
def start_reminder_thread(chat_id):
    if not reminder_started:
        reminder_started = True
        reminder_thread = threading.Thread(target=send_reminder, args=(chat_id, ))
        reminder_thread.start()

bot.polling(none_stop=True)

