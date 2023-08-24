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
from sqlalchemy import cast, Date

session = Session()

TOKEN = '6177637545:AAH-qY4PytR-CGyCrG_OvpTrckaHpZ5Kv68'
bot = telebot.TeleBot(TOKEN)
calendar = Calendar(language=ENGLISH_LANGUAGE)
calendar_1 = CallbackData('calendar_1', 'action', 'year', 'month', 'day')
calendar_2 = CallbackData('calendar_2', 'action', 'year', 'month', 'day')
now = datetime.datetime.now()

chat_id = 0

@bot.message_handler(commands=['start', 'refresh'])
def send_welcome(message):
    keyboard = types.ReplyKeyboardMarkup(True)
    # button1 = types.KeyboardButton('/add_task')
    # button2 = types.KeyboardButton('/show_task')
    button3 = types.KeyboardButton('/help')
    # keyboard.add(button1)
    # keyboard.add(button2)
    keyboard.add(button3)
    start_reminder_thread(message.chat.id)
    bot.send_message(message.chat.id, 'Hello, ' + message.from_user.first_name + '! This is a NUSPE Manager bot!', reply_markup=keyboard)

@bot.message_handler(commands=['help'])
def send_hello(message):
    bot.reply_to(message, "Please add in a task, the deadlines, and who you assign the task to!")
    
@bot.message_handler(commands=['add_task'])
def add_tasks(message):
    bot.send_message(message.chat.id, 'Which date do you want to add a task to?', 
            reply_markup=calendar.create_calendar(
                name=calendar_1.prefix,
                year=now.year,
                month=now.month)
            )
    
    
@bot.message_handler(commands=['huyen'])
def reply_to_huyen(message):
    bot.reply_to(message, "Anh yêu em nhiều lắm Huyền ơi!!! Anh chỉ muốn hôn em và nắm tay em nhiều hơn nữa :)))")
    
@bot.message_handler(commands=['fuck_you'])
def reply_to_fu(message):
    bot.reply_to(message, 'Do not worry brother, NUSPE will never leave you or fk you alone <3')
    

# the function is a callback request handler. It is called when you click on the calendar buttons
@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_1.prefix))
def callback_inline(call: types.CallbackQuery):
    name, action, year, month, day = call.data.split(calendar_1.sep)
    date = calendar.calendar_query_handler(bot=bot, call=call, name=name, action=action, year=year, month=month, day=day)
    if action == 'DAY':
        c_date = date.strftime("%d.%m.%Y")
        msg = bot.send_message(chat_id=call.message.chat.id, text=f'You chose {c_date}, please enter your plan.\nFormat your plan this way: task_name|assignee|remarks: ')
        bot.register_next_step_handler(msg, lambda message: add_task(message, chat_id=call.message.chat.id, c_date=c_date))
    elif action == 'CANCEL':
        bot.send_message(chat_id=call.message.chat.id, text='🚫 Cancelled')
        
@bot.message_handler(commands=['showing'])
def test_show_task(message):
    bot.send_message(message.chat.id, 'Select start date', 
            reply_markup=calendar.create_calendar(
                name=calendar_2.prefix,
                year=now.year,
                month=now.month)
            )
    
@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_2.prefix))
def callback_1(call: types.CallbackQuery):
    name, action, year, month, day = call.data.split(calendar_1.sep)
    date = calendar.calendar_query_handler(bot=bot, call=call, name=name, action=action, year=year, month=month, day=day)
    if action == 'DAY':
        bot.send_message(chat_id=call.message.chat.id, 'Clicked')
        # bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='Clicked')
        # bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.id, text='Clicked')

@bot.message_handler(commands=['show_task'])
def show_tasks(message):
    print(message)
    print(message.text.split(' '))
    filtered = session.query(Tasks).filter_by(chat_id=str(message.chat.id), status='ongoing').all()
    print('Show tasks called', message.chat.id)
                
    if filtered == []:
        bot.send_message(message.chat.id, 'No task is available now')

    dates = defaultdict(list)
    for value in filtered:
        date = value.task_deadlines
        dates[date].append(value)
        
    print(dates)
        
    for date, tasks in dates.items():
        tasks_text = '\n'.join(f'- {task.task_name} assigned to {task.task_assignee}' for task in tasks)
        text = f'Tasks for {date}:'
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        for task in tasks:
            # button = types.InlineKeyboardButton(text=f'View: {task.task_name}', callback_data=f'delete@@{task.task_name}@@{task.task_deadlines}')
            button = types.InlineKeyboardButton(text=f'View: {task.task_name}', callback_data=f"select@@{task.task_id}")
            keyboard.add(button)
        bot.send_message(message.chat.id, text, reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith('select@@'))
def view_task(call):
    task_id = call.data.split('@@')[1]
    task = session.query(Tasks).filter_by(task_id=task_id).one_or_none()
    if task:
        view_button = types.InlineKeyboardButton(text=f'Edit task', callback_data=f'edit@@')
        delete_button = types.InlineKeyboardButton(text=f'Delete task', callback_data=f'delete@@')
        cancel_button = types.InlineKeyboardButton(text=f'Cancel', callback_data='cancel')
        
        keyboard = types.InlineKeyboardMarkup(
            [
                [view_button, delete_button], [cancel_button]
            ]
        )
        bot.send_message(call.message.chat.id, f'View {task.task_name}', reply_markup=keyboard)

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
    pass
    # print(call.data.split('@@'))
    # _, task, date = call.data.split('@@')
    # delete_task(call.message.chat.id, date, task)
    # bot.answer_callback_query(call.id, text=f'Task "{task}" on {date} deleted. \nPlease restart by typing /show_task again')


# the function of adding a new task
def add_task(message, chat_id, c_date):
    try:
        add_todo(chat_id, c_date, message)
        text = f'Task successfully registered on {c_date}'
        bot.send_message(chat_id=chat_id, text=text)
    except:
        bot.send_message(chat_id=chat_id, text='Error occurred! Please format your plan this way: \n[task name]|[assignee]|[remarks]\nLeave blank but keep the | if do not have')
        

# the function adds a task to the todos dictionary
def add_todo(chat_id, c_date, message):
    task, assignee, remarks = message.text.split('|')
    print(c_date)
    date_obj = datetime.datetime.strptime(c_date, "%d.%m.%Y")
    obj = Tasks(
        chat_id=chat_id, 
        task_name=task, 
        task_assignee=assignee, 
        task_deadlines=date_obj, 
        task_remarks=remarks
    )
    session.add(obj)
    session.commit()
        
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
    reminder_thread = threading.Thread(target=send_reminder, args=(chat_id, ))
    reminder_thread.start()

bot.polling(none_stop=True)

