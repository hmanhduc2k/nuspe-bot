from telebot import types

def start(bot, message):
    keyboard = types.ReplyKeyboardMarkup(True)
    bot.send_message(message.chat.id, 'Hello, ' + message.from_user.first_name + '! This is a NUSPE Manager bot!', reply_markup=keyboard)

def attach(bot_instance):
    @bot_instance.message_handler(commands=['start', 'refresh'])
    def handle_start(message):
        start(bot_instance, message)

# @bot.message_handler(commands=['start', 'refresh'])
# def send_welcome(message):
    
#     start_reminder_thread(message.chat.id)
#     bot.send_message(message.chat.id, 'Hello, ' + message.from_user.first_name + '! This is a NUSPE Manager bot!', reply_markup=keyboard)