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
