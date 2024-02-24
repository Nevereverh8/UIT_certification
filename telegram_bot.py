# -*- coding: utf-8-sig -*-
import datetime
from dateutil.relativedelta import relativedelta
import math
import telebot
import json
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from db_requests import db
from db_requests import pending_orders
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP

# telegram settings
with open('config.json', 'r') as file:
    content = json.load(file)
    token = content['tg_token']
    employee_chat_id = content['employee_chat_id']
    print('bot token: ' + token)
    print('employee_chat_id: ' + employee_chat_id)

bot = telebot.TeleBot(token)

# global dicts and lists
sessions = {}
ru_step = {'year': 'год',
           'month': 'месяц',
           'day': 'день'
            }


# callback legend
# c; - customer side
#   ;o - order related
#     ;№ - to step №
#     ;s - service related
#   ;r - review related
#
#
# e; - employee side
#
# a; - admin side
#
#




### static functions section


# func to icrease or decrease anything in sessions by one
def add_sub(chat_id, thing, sign):
    if sign == '-' and sessions[chat_id]['services_dict'][thing]['amount'] != 1:
        sessions[chat_id]['services_dict'][thing]['amount'] -= 1
        return sessions[chat_id]['services_dict'][thing]['amount']
    elif sign == '+':
        sessions[chat_id]['services_dict'][thing]['amount'] += 1
    else:
        return 1
    return sessions[chat_id]['services_dict'][thing]['amount']


# # time availiable to do service at date
# def time_availiable(date, order_time, services_dict):
#     time_pool = db.get_time_availiable(date, order_time, services_dict)[0]
#     # there should be SQL request somehow checking if there enought spare time and equipment any employee have?
#     # that should return time interval availiable at this day
#     return time_pool


# price calc
def total_price(chat_id):
    services_d = db.get_services(all=True)
    total_sum = 0
    for service in sessions[chat_id]['services_dict']:
        total_sum += services_d[service]['price'] * sessions[chat_id]['services_dict'][service]['amount']
    return total_sum


def time_req(chat_id):
    services_d = db.get_services(all=True)
    t = 0
    for service in sessions[chat_id]['services_dict']:
        # print(f"{services_d[service]['time']}  and amount is {sessions[chat_id]['services_dict'][service]['amount']}")
        t += services_d[service]['time'] * sessions[chat_id]['services_dict'][service]['amount']
    hours_types = ('ов', '', 'а')
    if t == 1:
        h = ''
    elif t >= 5:
        h = 'ов'
    else:
        h = 'а'
    return t, h


def current_services_list(chat_id):
    s_list = 'Ваш заказ:'
    for service in sessions[chat_id]['services_dict']:
        if service != 'Базовая цена':
            s_list += f"\n{service} X {sessions[chat_id]['services_dict'][service]['amount']}"
    t = time_req(chat_id)
    s_list += f'\nДлительность: {t[0]} час{t[1]}'
    if 'date' in sessions[chat_id] and 'time' in sessions[chat_id]:
        s_list += f"\nДата и время: {sessions[chat_id]['date']} {sessions[chat_id]['time']} "
    s_list += f'\nИтого {total_price(chat_id)} руб.'
    return s_list


# call parsers
def sim_parse(call):            # chat_id, message_id, data = sim_parse(call)
    return call.message.chat.id, call.message.id, call.data


def adv_parse(call):            # chat_id, message_id, data, text, keyb = adv_parse(call)
    return call.message.chat.id, call.message.id, call.data, call.message.text, call.message.reply_markup

### end of static functions section




### static keyboards and keygens section


start_menu_keyb = InlineKeyboardMarkup()
start_menu_keyb.add(InlineKeyboardButton('Заказать клининг', callback_data='c;o;start'))
start_menu_keyb.add(InlineKeyboardButton('Отзывы', callback_data='c;r;show'))
start_menu_keyb.add(InlineKeyboardButton('Частые вопросы', callback_data='c;o;faq'))

nav_keyb = InlineKeyboardMarkup()
nav_keyb.add(InlineKeyboardButton('К комнатам/санузлам', callback_data='c;o;start'))
nav_keyb.add(InlineKeyboardButton('К доп. услугам', callback_data='c;o;1'),
             InlineKeyboardButton('К дате/времени', callback_data='c;o;2'))
nav_keyb.add(InlineKeyboardButton('К адресу/телефону', callback_data='c;o;3'))
nav_keyb.add(InlineKeyboardButton('Заказать', callback_data='c;o;5'))






def main_calc_keyb_gen(n_rooms, n_baths):
    keyb = InlineKeyboardMarkup()
    keyb.add(InlineKeyboardButton('+', callback_data='c;o;r;+'),
             InlineKeyboardButton('+', callback_data='c;o;b;+'))
    keyb.add(InlineKeyboardButton('Комнаты: '+str(n_rooms), callback_data='c;o;r;a'),
             InlineKeyboardButton('Санузлы: '+str(n_baths), callback_data='c;o;b;a'))
    keyb.add(InlineKeyboardButton('-', callback_data='c;o;r;-'),
             InlineKeyboardButton('-', callback_data='c;o;b;-'))
    keyb.add(InlineKeyboardButton('Продолжить', callback_data='c;o;1'),
             InlineKeyboardButton('Назад', callback_data='c;main_menu'))
    return keyb


def services_keyb_gen():
    services_keyb = InlineKeyboardMarkup()
    services_dict = db.get_services()
    services = list(services_dict.keys())
    l = math.ceil(len(services)/2)
    for i in range(l):
        if (i+1)*2 <= len(services):
            services_keyb.add(InlineKeyboardButton(services[2*i],
                                                   callback_data=f"c;o;s;{services[2*i]};{services_dict[services[2*i]]['is_scaleable']}"),
                              InlineKeyboardButton(services[2*i+1],
                                                   callback_data=f"c;o;s;{services[2*i+1]};{services_dict[services[2*i+1]]['is_scaleable']}"))
        else:
            services_keyb.add(InlineKeyboardButton(services[2*i],
                                                   callback_data=f"c;o;s;{services[2*i]};{services_dict[services[2*i]]['is_scaleable']}"))

    services_keyb.add(InlineKeyboardButton('Продолжить', callback_data='c;o;2'),
             InlineKeyboardButton('Назад', callback_data='c;o:start'))
    return services_keyb

### end of static keyboards and keygens section





# start main menu
@bot.message_handler(commands=['start'])
def start(message):
    sessions[message.chat.id] = {}
    m = bot.send_message(message.chat.id, 'КлинниБогини приветствует вас', reply_markup=start_menu_keyb)
    sessions[message.chat.id]['last_bot_message'] = m.message_id

# step 3 adr and tel handler
@bot.message_handler(content_types=['text'])
def tel_adr(message):
    chat_id = message.chat.id
    print(message.text)
    new_text = current_services_list(chat_id) + '\n'
    if chat_id in sessions:
        if message.text.isdigit():
            sessions[chat_id]['tel'] = message.text
        else:
            sessions[chat_id]['adress'] = message.text
        if 'adress' in sessions[chat_id] and 'tel' in sessions[chat_id]:
            new_text += f"\n Ваш адрес:{sessions[chat_id]['adress']} \nВаш телефон: {sessions[chat_id]['tel']}\n!Проверьте правильность введенных данных!"
            keyb = InlineKeyboardMarkup()
            keyb.add(InlineKeyboardButton('Подтвердить', callback_data='c;o;4'))
            bot.edit_message_text(new_text,
                                  chat_id,
                                  sessions[chat_id]['last_bot_message'],
                                  reply_markup=keyb
                                  )
        elif 'adress' in sessions[message.chat.id]:
            new_text += f"\nВаш адрес:{sessions[chat_id]['adress']} \nОтправьте ваш телефон(9 цифр) в сообщении (+375 ХХХХХХХХХ)"
            bot.edit_message_text(new_text,
                                  chat_id,
                                  sessions[chat_id]['last_bot_message'],
                                  )
        elif 'tel' in sessions[chat_id]:
            new_text += f"\nВаш телефон: {sessions[message.chat.id]['tel']} \nОтправьте ваш адрес в сообщении"
            bot.edit_message_text(new_text,
                                  chat_id,
                                  sessions[chat_id]['last_bot_message'],
                                  )
        new_text += '\nЧтобы изменить адресс или телефон, отправьте его ещё раз'
        bot.delete_message(chat_id, message.id)



        new_text += '\n Отправьте ваш адрес и телефон(9 цифр) двумя отдельными сообщениями(телефон +375 ХХХХХХХХХ)'


# main menu
@bot.callback_query_handler(func=lambda call: call.data == 'c;main_menu')
def call_start(call):
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=sessions[call.message.chat.id]['last_bot_message'],
                          text='КлинниБогини приветствует вас',
                          reply_markup=start_menu_keyb)


# step 0: rooms and baths choice
@bot.callback_query_handler(func=lambda call: call.data == 'c;o;start')
def order_start(call):
    bot.answer_callback_query(callback_query_id=call.id)
    chat_id, message_id, data = sim_parse(call)
    if 'services_dict' not in sessions[chat_id]:
        sessions[chat_id]['services_dict'] = {}
        sessions[chat_id]['services_dict']['Комната'],sessions[chat_id]['services_dict']['Санузел'], \
        sessions[chat_id]['services_dict']['Базовая цена'] = {'amount': 1}, {'amount': 1}, {'amount': 1}
        keyb = main_calc_keyb_gen(1, 1)
    else:
        keyb = main_calc_keyb_gen(sessions[chat_id]['services_dict']['Комната'], sessions[chat_id]['services_dict']['Санузел'])
    t_price = total_price(chat_id)
    bot.edit_message_text(chat_id=chat_id,
                          message_id=message_id,
                          text=f'Выберите количество комнат и санузлов чтобы мы могли рассчитать приблизительную стоимость.\nСтоимость: {t_price} руб. \n',
                          reply_markup=keyb)



# step 0 calc buttons
@bot.callback_query_handler(func=lambda call: call.data in ('c;o;r;+', 'c;o;b;+', 'c;o;r;-', 'c;o;b;-',))
def order_main_add_sub(call):
    bot.answer_callback_query(callback_query_id=call.id)
    chat_id, message_id, data, text, keyb = adv_parse(call)
    sign = data[-1]
    # math
    if data.split(';')[2] == 'r':
        amount = add_sub(chat_id, 'Комната', sign)
        keyb.keyboard[1][0] = InlineKeyboardButton('Комнаты: '+str(amount), callback_data='c;o;r;a')
    elif data.split(';')[2] == 'b':
        amount = add_sub(chat_id, 'Санузел', sign)
        keyb.keyboard[1][1] = InlineKeyboardButton('Санузлы: '+str(amount), callback_data='c;o;b;a')

    t_price = total_price(chat_id)
    new_text = f'Выберите количество комнат и санузлов чтобы мы могли рассчитать приблизительную стоимость.\nСтоимость: {t_price} руб.'
    if new_text != text:
        bot.edit_message_text(chat_id=chat_id,
                              message_id=message_id,
                              text=new_text,
                              reply_markup=keyb
                              )


# step 1: additional services
@bot.callback_query_handler(func=lambda call: call.data == 'c;o;1' or ''.join(call.data.split(';')[:3]) == 'cos')
def services(call):
    bot.answer_callback_query(callback_query_id=call.id)
    chat_id, message_id, data, text, keyb = adv_parse(call)
    print(data)
    services_d = db.get_services()
    # main service menu
    if data == 'c;o;1':
        new_text = current_services_list(
            chat_id) + '\nЖелаете ли выбрать какие-либо дополнительные услуги?\n(Нажмите на услугу еще раз чтобы отказаться от неё)'
        bot.edit_message_text(chat_id=chat_id,
                              message_id=message_id,
                              text=new_text,
                              reply_markup=services_keyb_gen()
                              )

    # unscaleable handle
    elif ''.join(data.split(';')[:3]) == 'cos' and data.split(';')[4] == '0': # flag 5 is 'is_scaleable'
        service = data.split(';')[3]
        if service in sessions[chat_id]['services_dict']:
            if sessions[chat_id]['services_dict'][service]['amount'] == 1:
                sessions[chat_id]['services_dict'].pop(service)
        else:
            sessions[chat_id]['services_dict'][service] = {'amount': 1}
        new_text = current_services_list(chat_id) + '\nЖелаете ли выбрать какие-либо дополнительные услуги?\n(Нажмите на услугу еще раз чтобы отказаться от неё)'
        bot.edit_message_text(chat_id=chat_id,
                              message_id=message_id,
                              text=new_text,
                              reply_markup=services_keyb_gen()
                              )

    # scaleable handle
    elif ''.join(data.split(';')[:3]) == 'cos' and data.split(';')[4] == '1': # flag 5 is 'is_scaleable'
        service = data.split(';')[3]
        if len(data.split(';')) == 5:  # if in main menu
            time_req = services_d[service]['time']
            price = services_d[service]['price']
            keyb = InlineKeyboardMarkup()
            for i in range(1, 6):
                keyb.add(InlineKeyboardButton(str(i*2-1), callback_data=f"c;o;s;{service};1;{str(i*2-1)}"),
                         InlineKeyboardButton(str(i*2), callback_data=f"c;o;s;{service};1;{str(i*2)}"),)
            if service in sessions[chat_id]['services_dict']:
                keyb.add(InlineKeyboardButton('Отменить услугу', callback_data=f"c;o;s;{service};1;0"),
                         InlineKeyboardButton('Назад', callback_data='c;o;1'))
            else:
                keyb.add(InlineKeyboardButton('Назад', callback_data='c;o;1'))

            bot.edit_message_text(chat_id=chat_id,
                                  message_id=message_id,
                                  text=f'Услуга \"{service}\" занимает {time_req} часа(ов) и стоит {price} руб. за штуку/час (глажка белья измеряется за час, остальное как штуки) \n Выберите количество услуг',
                                  reply_markup=keyb)
        else:  # if in scaleable_handle_menu
            if len(data.split(';')) == 6:
                if data.split(';')[5] == '0':
                    if service in sessions[chat_id]['services_dict']:
                        sessions[chat_id]['services_dict'].pop(service)
                else:
                    sessions[chat_id]['services_dict'][service] = {'amount': int(data.split(';')[5])}
                new_text = current_services_list(chat_id) + '\nЖелаете ли выбрать какие-либо дополнительные услуги?\n(Нажмите на услугу еще раз чтобы отказаться от неё)'
                bot.edit_message_text(chat_id=chat_id,
                                      message_id=message_id,
                                      text=new_text,  # remake later
                                      reply_markup=services_keyb_gen()
                                      )


# step 2: date and time selection
@bot.callback_query_handler(func=lambda call: call.data == 'c;o;2' )
def date_time_selection(call):
    chat_id, message_id, data, text, keyb = adv_parse(call)
    bot.answer_callback_query(callback_query_id=call.id)
    calendar, step = DetailedTelegramCalendar(min_date=datetime.date.today(), # here should be closest date where employees free
                                              max_date=datetime.date.today() + relativedelta(months=2),
                                              locale='ru').build()
    bot.edit_message_text(chat_id=chat_id,
                          message_id=message_id,
                          text=f"Выберите {ru_step[LSTEP[step]]}",
                          reply_markup=calendar)


# step2: calendar and time handler
@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def cal(c):
    chat_id, message_id, data, text, keyb = adv_parse(c)
    result, key, step = DetailedTelegramCalendar(locale='ru',
                                                 min_date=datetime.date.today(),
                                                 max_date=datetime.date.today() + relativedelta(months=2),
                                                 ).process(data)
    if not result and key:
        bot.edit_message_text(f"Выберите {ru_step[LSTEP[step]]}",
                              chat_id,
                              message_id,
                              reply_markup=key)
    elif result:
        req_t = time_req(chat_id)
        availiability_data = db.get_time_availiable('.'.join(str(result).split('-')), req_t[0], sessions[chat_id]['services_dict'])

        keyb = InlineKeyboardMarkup()

        # there is time availiable at this day
        if availiability_data:
            time_pool = availiability_data[0]
            new_text = f"Вы выбрали дату {result} \nДлительность: {req_t[0]} час{req_t[1]} \nВыберите время которое вам подходит"
            sessions[chat_id]['date'] = '.'.join(str(result).split('-'))
            # time keyb gen
            keyb.row_width = 4
            btn_list = []
            for d_time in time_pool:
                if d_time % 2 == 0:
                    t = str(d_time//2) + ':00'
                else:
                    t = str(d_time//2) + ':30'
                btn_list.append(InlineKeyboardButton(f'{t}', callback_data=f'c;o;3;{t}'))

            for i in range(4-len(btn_list) % 4):
                btn_list.append(InlineKeyboardButton(f' ', callback_data='text_btn'))
            for i in range(len(btn_list)//4):
                keyb.add(*btn_list[i*4:i*4+4])

        # there is no time availiable at this day or not enough equip
        else:
            new_text = f"К сожалению в этот день все наши специалисты заняты, выберите другую дату, пожалуйста \n "
            keyb.add(InlineKeyboardButton('Выбрать другой день', callback_data='c;o;2'))
        bot.edit_message_text(new_text,
                              chat_id,
                              message_id,
                              reply_markup=keyb)

# step 3 adress and tel collection
@bot.callback_query_handler(func=lambda call: call.data[:5] == 'c;o;3')
def adress_and_phone(call):
    chat_id, message_id, data = sim_parse(call)
    # time recording
    if len(data.split(';')) == 4:
        sessions[chat_id]['time'] = data.split(';')[3]
    if 'tel' in sessions[chat_id]:
        sessions[chat_id].pop('tel')
    if 'adress' in sessions[chat_id]:
        sessions[chat_id].pop('adress')
    new_text = current_services_list(chat_id)
    new_text += '\n Отправьте ваш адрес и телефон(9 цифр) двумя отдельными сообщениями(телефон +375 ХХХХХХХХХ)'
    bot.edit_message_text(new_text,
                          chat_id,
                          message_id)
    # Z-z-z


# step 4 confirmation
@bot.callback_query_handler(func=lambda call: call.data[:5] == 'c;o;4')
def confirmation(call):
    chat_id, message_id, data = sim_parse(call)
    new_text = current_services_list(chat_id)
    new_text += f"\n Ваш адрес:{sessions[chat_id]['adress']} \nВаш телефон: {sessions[chat_id]['tel']}\nПроверьте ваш заказ и нажмите закзать для начала обработки заказа"

    bot.edit_message_text(new_text,
                          chat_id,
                          message_id,
                          reply_markup=nav_keyb)

# step 5 order_sending


@bot.callback_query_handler(func=lambda call: True)
def unknown_call(call):
    print('unknown call:  '+call.data)


print("\nready")

bot.infinity_polling()
