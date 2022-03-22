import json
from random import randint
from datetime import datetime

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

ikb = InlineKeyboardButton
ikm = InlineKeyboardMarkup
start_menu = ikm([
    [
        ikb("info", callback_data='info'),
        ikb("shop", callback_data='shop')
    ],
    [
        ikb("map", callback_data='map'),
        ikb("stats", callback_data='stats')
    ]
])

shop_list = [
    {"name": "Корова", "cost": 200, "value": 999, "emoji": "🐮"},
    {"name": "Барашек", "cost": 100, "value": 999, "emoji": "🐏"}
]

import config

json_base = {}

apple = "🍏"
tree = "🌳"


def start(update, context):
    json_base[update.effective_chat.id] = {}
    farm = json_base[update.effective_chat.id]["farm"] = {}
    farm["stats"] = {"nick": update.effective_message.chat.full_name, "regDate": datetime.today().strftime('%Y-%m-%d'),
                     "score": 1000}
    farm["map"] = []
    farm["inv"] = []
    update.message.reply_text("Start", reply_markup=start_menu)


def start_new(update, context):
    update.callback_query.edit_message_text("Start", reply_markup=start_menu)


def buttons(update, context):
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    qd = query.data
    qe = query.edit_message_text
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    if qd == "info":
        st = json_base[update.effective_chat.id]["farm"]["stats"]
        _inv = json_base[update.effective_chat.id]["farm"]["inv"]
        inv = ""
        for x in _inv:
            inv = inv + "%s %s, цена: %s. Кол-во: %s \n" % (x["emoji"], x["name"], str(x["cost"]), str(x["value"]))
        update.callback_query.edit_message_text("""
        Ник: %s
        Время сохранения: %s
        Деньги: %s
        В загонах: 
        %s
        ------
        В инвентаре: 
        %s
        
        """ % (st["nick"], st["regDate"], st["score"], "", inv)
                                                , reply_markup=start_menu)
    elif qd == "shop":
        shop(update, context)
    elif qd == "map":
        map_generate(update, context, "map")
    elif qd == "stats":
        pass
    elif qd == "start":
        start_new(update, context)
    elif qd[:3] == "map":
        x = int(qd[3:qd.find("|")])
        y = int(qd[qd.find("|") + 1:])
        cell_map = json_base[update.effective_chat.id]["farm"]["map"][x][y].text
        if cell_map == tree:
            json_base[update.effective_chat.id]["farm"]["map"][x][y].text = " "
            json_base[update.effective_chat.id]["farm"]["stats"]["score"] += 20
        elif cell_map == apple:
            json_base[update.effective_chat.id]["farm"]["map"][x][y].text = " "
            json_base[update.effective_chat.id]["farm"]["stats"]["score"] += 100
        map_generate(update, context, "map")
    elif qd[:9] == "shop_buy_":
        x = qd[9:]
        z = None
        for y in shop_list:
            if y["name"] == x:
                z = y
        scores = json_base[update.effective_chat.id]["farm"]["stats"]["score"]
        if z["cost"] <= scores:
            json_base[update.effective_chat.id]["farm"]["stats"]["score"] -= z["cost"]
            for x in shop_list:
                if x["name"] == z["name"]:
                    x["value"] -= 1
            shop(update, context)
            flag = False
            for inv in json_base[update.effective_chat.id]["farm"]["inv"]:
                if inv['name'] == z["name"]:
                    inv["value"] += 1
                    flag = True
            if not flag:
                json_base[update.effective_chat.id]["farm"]["inv"].append(
                    {"name": z["name"], "cost": z["cost"] / 2, "value": 1, "emoji": z["emoji"]})
        else:
            pass # add mesage about not enough money



def shop(update, context):
    keyboard = []
    for x in shop_list:
        keyboard.append([ikb("%s %s, цена: %s. Кол-во: %s"
                             % (x["emoji"], x["name"],
                                x["cost"], x["value"]),
                             callback_data=("shop_buy_" + x["name"]))])
    keyboard.append([ikb("Start", callback_data="start")])
    update.callback_query.edit_message_text("Shop", reply_markup=ikm(keyboard))


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
    id = update.effective_chat.id
    msg_text = update.effective_message.text
    value = context.user_data.get("quiz_state", False)
    if not value:
        update.message.reply_text("Вопрос ещё не был задан")
        return
    elif value == 1:
        context.user_data["quiz_state"] = 2
        json_base[id]["quiz1"]["answ1"] = msg_text
        update.message.reply_text("Введите второй ответ!")


# 11x8
def showAll(update, context):
    update.message.reply_text(str(json_base))


def map_generate_items():
    i = randint(1, 100)
    if 0 <= i <= 50:
        return " "
    elif 70 <= i <= 90:
        return tree
    elif 91 <= i <= 100:
        return apple
    return " "


def map_generate(update, context, tag):
    x = json_base[update.effective_chat.id]["farm"]["map"]
    if x == []:
        axle_x = 8
        axle_y = 10
        for v in range(axle_y):
            x.append([])
            for b in range(axle_x):
                x[v].append(ikb(map_generate_items(), callback_data=(tag + str(v) + '|' + str(b))))
        x.append([ikb("Start", callback_data="start")])

    update.callback_query.edit_message_text("Map_generate", reply_markup=ikm(x))


if __name__ == '__main__':
    updater = Updater(config.telegram_token, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('save', save))
    dp.add_handler(CommandHandler('load', load))
    dp.add_handler(CommandHandler('showAll', showAll))
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CallbackQueryHandler(buttons))

    dp.add_handler(MessageHandler((Filters.text & (~ Filters.command)), text))
    updater.start_polling()
    updater.idle()
