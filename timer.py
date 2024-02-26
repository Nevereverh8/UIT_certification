from db_requests import pending_orders
import time
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telegram_bot import token, employee_chat_id, delay

bot = telebot.TeleBot(token)

timers_list = {}
tick = 5
while True:
    p = pending_orders.copy()
    if timers_list:
        print(timers_list)
    for i in p:
        if not p[i]['sent']:
            if i not in timers_list:
                timers_list[i] = delay - tick
            elif timers_list[i] <= 0:
                p[i]['sent'] = True
                text = f"{p[i]['text']}"
                bot.edit_message_text(chat_id=i,
                                      message_id=p[i]['last_bot_message'],
                                      text='Ваш заказ обрабатывается\n' + '\n'.join(
                                          p[i]['text'].split('\n')[1:]))
                employee_message = bot.send_message(employee_chat_id,
                                                    text,
                                                    reply_markup=p[i]['keyb'])
                p[i]['employee_message_id'] = employee_message.message_id

                timers_list.pop(i)
            else:
                timers_list[i] -= tick
        else:
            pending_orders.pop(i)
            if i in timers_list:
                timers_list.pop(i)
    time.sleep(tick)
