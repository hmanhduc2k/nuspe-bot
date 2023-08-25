def reply_to_help(bot, message):
    bot.reply_to(message, "Please add in a task, the deadlines, and who you assign the task to!")
    
def attach(bot_instance):
    @bot_instance.message_handler(commands=['help'])
    def handle_start(message):
        reply_to_help(bot_instance, message)