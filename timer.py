from db_requests import pending_orders
import time
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telegram_bot import token, employee_chat_id, delay

bot = telebot.TeleBot(token)

timers_list = {}
tick = 5
while True:
    if timers_list:
        print(timers_list)
    for i in pending_orders:
        if not pending_orders[i]['sent']:
            if i not in timers_list:
                timers_list[i] = delay
            elif timers_list[i] <= 0:
                pending_orders[i]['sent'] = True
                text = f"{pending_orders[i]['text']}"
                employee_message = bot.send_message(employee_chat_id,
                                                    text,
                                                    reply_markup=pending_orders[i]['keyb'])
                pending_orders[i]['employee_message_id'] = employee_message.message_id
                timers_list.pop(i)
            else:
                timers_list[i] -= tick
    time.sleep(tick)
