import telebot
from telebot import types
from telebot_calendar import *
import telebot_calendar
import datetime
from datetime import timedelta
import schedule
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

todos = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    keyboard = types.ReplyKeyboardMarkup(True)
    button1 = types.KeyboardButton('/add_task')
    button2 = types.KeyboardButton('/show_task')
    button3 = types.KeyboardButton('/help')
    keyboard.add(button1)
    keyboard.add(button2)
    keyboard.add(button3)
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
        msg = bot.send_message(chat_id=call.message.chat.id, text=f'You chose {c_date}, please enter your plan: ')
        bot.register_next_step_handler(msg, lambda message: add_task(message, chat_id=call.message.chat.id, c_date=c_date))
    elif action == 'CANCEL':
        bot.send_message(chat_id=call.message.chat.id, text='🚫 Cancelled')
    
@bot.message_handler(commands=['show_task'])
def show_tasks(message):
    filtered = []
    print('Show tasks called', message.chat.id)
    with open('data/tasks.csv', 'r') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            if row['chat_id'] == str(message.chat.id) and row['status'] == 'ongoing':
                filtered.append(row)
                
        if filtered == []:
            bot.send_message(message.chat.id, 'No task is available now')
    
        dates = defaultdict(list)
        for value in filtered:
            date = value['task_deadlines']
            print(date)
            dates[date].append(value['task_name'] + ', assigned to ' + value['task_assignee'])
            
        print(dates)
            
        for date, tasks in dates.items():
            tasks_text = '\n'.join(f'- {task}' for task in tasks)
            text = f'Tasks for {date}:\n{tasks_text}'
            keyboard = types.InlineKeyboardMarkup()
            for task in tasks:
                button = types.InlineKeyboardButton(text=f'❌', callback_data=f'delete:{date}:{task}')
                keyboard.add(button)
            bot.send_message(message.chat.id, text, reply_markup=keyboard)

# task deletion function
def delete_task(chat_id, c_date, task):
    with open('data/tasks.csv', 'a') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow([chat_id, task, 'None', c_date, 'None'])
    # if todos.get(chat_id) is not None:
    #     if todos[chat_id].get(c_date) is not None:
    #         todos[chat_id][c_date].remove(task)
    #         if len(todos[chat_id][c_date]) == 0:
    #             del todos[chat_id][c_date]
    #         if len(todos[chat_id]) == 0:
    #             del todos[chat_id]
        

# deletes the task and displays a message about the successful deletion of this task.
@bot.callback_query_handler(func=lambda call: call.data.startswith('delete:'))
def delete_callback(call):
    _, date, task = call.data.split(':')
    delete_task(call.message.chat.id, date, task)
    bot.answer_callback_query(call.id, text=f'Task "{task}" on {date} deleted')


# the function of adding a new task
def add_task(message, chat_id, c_date):
    add_todo(chat_id, c_date, message)
    text = f'Task successfully registered on {c_date}'
    bot.send_message(chat_id=chat_id, text=text)

# the function adds a task to the todos dictionary
def add_todo(chat_id, c_date, message):
    task = message.text
    # if todos.get(chat_id) is not None:
    #     if todos[chat_id].get(c_date) is not None:
    #         todos[chat_id][c_date].append(task)
    #     else:
    #         todos[chat_id][c_date] = [task]
    # else:
    #     todos[chat_id] = {c_date: [task]}
    print(c_date)
    date_obj = datetime.strptime(c_date, "%d.%m.%Y")
    obj = Tasks(
        chat_id=chat_id, 
        task_name=task, 
        task_assignee='None', 
        task_deadlines=date_obj, 
        task_remarks='None'
    )
    session.add(obj)
    session.commit()
    with open('data/tasks.csv', 'a') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow([uuid.uuid4(), chat_id, task, 'None', c_date, 'None', 'ongoing'])
        
# def send_reminders():
#     now = datetime.now()
#     reminder_range = timedelta(minutes=1)
#     with open('data/tasks.csv', 'r') as csvfile:
#         csvreader = csv.DictReader(csvfile)
#         for row in csvreader:
#             if row['chat_id'] == str(message.chat.id) and row['status'] == 'ongoing':
#                 filtered.append(row)
#     events = 
#     for event in events:
#         event_date = event['event_date']
#         time_diff = event_date - now

#         if timedelta(days=0) < time_diff < reminder_range:
#             chat_id = event['chat_id']
#             days_until_event = time_diff.days
#             bot.send_message(chat_id, f"Reminder: Your event is in {days_until_event} days!")

# # Schedule reminders to be sent every day at a specific time
# schedule.every().day.at("10:00").do(send_reminders)

# while True:
#     schedule.run_pending()
#     time.sleep(1)

bot.polling(none_stop=True)
