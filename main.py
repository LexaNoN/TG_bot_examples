from uuid import uuid4
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import config
import json


def put(update, context):
    """Usage: /put value"""
    key = str(uuid4())
    # Здесь не используется context.args, 
    # т.к. значение может содержать пробелы.
    value = update.message.text.partition(' ')[2]

    # сохраняем значение в контекст
    context.user_data[key] = value
    # отправляем ключ пользователю
    update.message.reply_text(key)


def get(update, context):
    """Usage: /get uuid"""
    # отделяем идентификатор от команды
    key = context.args[0]

    # загружаем значение и отправляем пользователю
    value = context.user_data.get(key, 'Not found')
    update.message.reply_text(value)


def save(update, context):
    value = context.user_data
    with open('data.json', 'w') as outfile:
        json.dump(value, outfile)
    update.message.reply_text("saved " + str(value))


def load(update, context):
    with open('data.json') as json_file:
        context.user_data.update(json.load(json_file))
    update.message.reply_text("loaded " + str(context.user_data))

def text(update, context):
    id = update.effective_user.id
    value = context.user_data.get("quiz_state", False)
    if not value:
        update.message.reply_text("Вопрос ещё не был задан")
    elif value == 1:
        print("1")
        context.user_data.update("text", "")
        context.user_data.update("quiz_state", 2)
    elif value == 2:
        print("2")
    else:
        print("netu")

def quiz(update, context):
    context.user_data["quiz_state"] = 1
    update.message.reply_text("Введите текст!")


if __name__ == '__main__':
    updater = Updater(config.telegram_token, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('put', put))
    dp.add_handler(CommandHandler('get', get))
    dp.add_handler(CommandHandler('save', save))
    dp.add_handler(CommandHandler('load', load))
    dp.add_handler(CommandHandler('quiz', quiz))
    dp.add_handler(MessageHandler(Filters.text, text))
    updater.start_polling()
    updater.idle()
