from uuid import uuid4
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
import config
import json
from fpdf import FPDF
import os
from random import randint

json_base = {}


def start(update, context):
    json_base[update.message.chat.id] = {}
    update.message.reply_text("Для начала опроса введите /quiz")


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
    id = update.message.chat.id
    msg_text = update.effective_message.text
    value = context.user_data.get("quiz_state", False)
    if not value:
        update.message.reply_text("Вопрос ещё не был задан")
        return
    elif value == 1:
        context.user_data["quiz_state"] = 2
        json_base[id]["quiz1"]["answ1"] = msg_text
        update.message.reply_text("Введите второй ответ!")
    elif value == 2:
        context.user_data["quiz_state"] = False
        json_base[id]["quiz1"]["answ2"] = msg_text
        update.message.reply_text("Спасибо за прохождение опроса!!")
        createPDF(
            [
                json_base[id]["quiz1"]["answ1"],
                json_base[id]["quiz1"]["answ2"]
            ], id)
        file_name = str(id) + ".pdf"
        context.bot.send_document(chat_id=update.message.chat.id,
                                  document=open(file_name, 'rb'),
                                  filename="answers.pdf")
        os.remove(file_name)


def createPDF(list, id):
    pdf = FPDF()
    pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
    pdf.set_font('DejaVu', '', 14)
    pdf.add_page()
    pdf.cell(200, 10, txt="Пример ПДФ опросника", ln=1, align='C')
    for i, j in enumerate(list):
        pdf.cell(200, 10, txt="Ответ номер " + str(i + 1) + ": " + j, ln=i + 2, align='C')
    pdf.output(str(id) + ".pdf", "F")

# 11x8
def showAll(update, context):
    update.message.reply_text(str(json_base))


def quiz(update, context):
    context.user_data["quiz_state"] = 1
    json_base[update.message.chat.id]["quiz1"] = {}
    update.message.reply_text("Введите первый ответ!")

def test_generate():
    i = randint(1, 100)
    if 0 <= i <= 50:
        return " "
    elif 70 <= i <= 90:
        return "🌳"
    elif 91 <= i <= 100:
        return "🍏"
    return " "

def test(update, context):
    x = []
    axle_x = 8
    axle_y = 11
    for v in range(axle_y):
        x.append([])
        for b in range(axle_x):
            x[v].append(InlineKeyboardButton(test_generate(), callback_data=(str(v) + str(b))))
    update.message.reply_text("123", reply_markup=InlineKeyboardMarkup(x))


if __name__ == '__main__':
    updater = Updater(config.telegram_token, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('put', put))
    dp.add_handler(CommandHandler('get', get))
    dp.add_handler(CommandHandler('save', save))
    dp.add_handler(CommandHandler('load', load))
    dp.add_handler(CommandHandler('quiz', quiz))
    dp.add_handler(CommandHandler('showAll', showAll))
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('test', test))

    dp.add_handler(MessageHandler((Filters.text & (~ Filters.command)), text))
    updater.start_polling()
    updater.idle()
