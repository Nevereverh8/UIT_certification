import runpy
from db_requests import db
import threading
import time
from db_requests import pending_orders
import datetime
import gspread
gc = gspread.service_account(filename='gspred_creds.json')



def tg_thread():
    runpy.run_module('telegram_bot', {}, "__main__")


def timer_thread():
    import timer


tg_thread = threading.Thread(target=tg_thread)
vk_thread = threading.Thread(target=timer_thread)
tg_thread.start()
vk_thread.start()


# # storage
# sh = gc.open('Клини богини').worksheet('Склад')
# cols = ['Название', 'Количество', 'Конец срока годности', 'Ед. изм.']
# sh.clear()
# sh.append_row(cols)
# sh.append_rows(db.get_storage(True, True))
#
# # orders:
# sh = gc.open('Клини богини').worksheet('Заказы')
# sh.clear()
# cols = db.get_columns('Orders')
# sh.append_row(cols)
# sh.append_rows(db.get_table('Orders'))
#
# print(sh)
# input()