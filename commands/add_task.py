from bot import bot

@bot.message_handler(commands=['huyen'])
def reply_to_huyen(message):
    bot.reply_to(message, "Anh yêu em nhiều lắm Huyền ơi!!! Anh chỉ muốn hôn em và nắm tay em nhiều hơn nữa :)))")