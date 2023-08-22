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
import csv
import uuid
from collections import defaultdict
from models import Tasks
from models import Session

session = Session()

TOKEN = '6177637545:AAH-qY4PytR-CGyCrG_OvpTrckaHpZ5Kv68'
bot = telebot.TeleBot(TOKEN)
calendar = Calendar(language=ENGLISH_LANGUAGE)
calendar_1 = CallbackData('calendar_1', 'action', 'year', 'month', 'day')
now = datetime.datetime.now()

chat_id = 0

@bot.message_handler(commands=['start'])
def send_welcome(message):
    keyboard = types.ReplyKeyboardMarkup(True)
    button1 = types.KeyboardButton('/add_task')
    button2 = types.KeyboardButton('/show_task')
    button3 = types.KeyboardButton('/help')
    keyboard.add(button1)
    keyboard.add(button2)
    keyboard.add(button3)
    chat_id = message.chat.id
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
    
@bot.message_handler(commands=['show_task'])
def show_tasks(message):
    filtered = session.query(Tasks).filter_by(chat_id=str(message.chat.id), status='ongoing').all()
    print('Show tasks called', message.chat.id)
                
    if filtered == []:
        bot.send_message(message.chat.id, 'No task is available now')

    dates = defaultdict(list)
    for value in filtered:
        date = value.task_deadlines
        print(date)
        dates[date].append(value)
        
    print(dates)
        
    for date, tasks in dates.items():
        tasks_text = '\n'.join(f'- {task.task_name} assigned to {task.task_assignee}' for task in tasks)
        text = f'Tasks for {date}:\n{tasks_text}'
        keyboard = types.InlineKeyboardMarkup()
        for task in tasks:
            button = types.InlineKeyboardButton(text=f'❌', callback_data=f'delete@@{task.task_name}@@{task.task_deadlines}')
            keyboard.add(button)
        bot.send_message(message.chat.id, text, reply_markup=keyboard)

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


# the function of adding a new task
def add_task(message, chat_id, c_date):
    try:
        add_todo(chat_id, c_date, message)
        text = f'Task successfully registered on {c_date}'
        bot.send_message(chat_id=chat_id, text=text)
        
        # Schedule the reminder to be sent every 10 minutes
        schedule.every(1).minutes.do(send_reminder, chat_id=chat_id)
    except:
        bot.send_message(chat_id=chat_id, text='Error occurred! Please format your plan this way: \n[task name]|[assignee]|[remarks]\nLeave blank but keep the | if do not have')
        
def send_reminder(chat_id):
    print('Printed statement')
    bot.send_message(chat_id=chat_id, text="This is a recurring reminder!")

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
        
bot.polling(none_stop=True)

# Start the scheduler loop
while True:
    schedule.run_pending()
    time.sleep(1)