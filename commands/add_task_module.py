
import telebot
from telebot import types
from telebot_calendar import *
from collections import defaultdict
from sqlalchemy import cast, Date, extract
from sqlalchemy.sql.expression import and_, or_

# @bot.message_handler(commands=['huyen'])
def reply_to_huyen(bot, message):
    bot.reply_to(message, "Anh yêu em nhiều lắm Huyền ơi!!! Anh chỉ muốn hôn em và nắm tay em nhiều hơn nữa :)))")
    
def attach(bot_instance):
    @bot_instance.message_handler(commands=['huyen'])
    def handle_start(message):
        reply_to_huyen(bot_instance, message)