import runpy
from db_requests import db
import threading
import time
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

while True:
    # Employee schedule:
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    week = [yesterday + datetime.timedelta(days=i) for i in range(7)]
    week = [str(day).replace('-', '.') for day in week]
    sh = gc.open('Клини богини').worksheet('График1')
    sh.clear()
    sh.append_row(["Клинер", "Номер заказа", "Время заказа", "Длительность уборки(часы)", "Адрес"])
    for date in ['2024.02.27','2024.02.28']:
        sh.append_row([date])
        schedule = db.get_schedule(date, 0)
        for employee in schedule:
            name = db.get_employee_name(employee)
            for order in schedule[employee]:
                adress = db.get_adress(schedule[employee][order]['client_id'])
                sh.append_row([name, order, schedule[employee][order]['time'], schedule[employee][order]['time_required'], adress])

    # storage sheet
    sh = gc.open('Клини богини').worksheet('Склад')
    cols = ['Название', 'Количество', 'Конец срока годности', 'Ед. изм.']
    sh.clear()
    sh.append_row(cols)
    sh.append_rows(db.get_storage(True, True))
    sh.update_cell(2,11,'Время последней синхронизации')
    sh.update_cell(3,11,str(datetime.datetime.now()))
    # print(sh.get_all_records(expected_headers=('Название', 'Количество', 'Конец срока годности', 'Ед. изм.')))

    # all other sheets
    sheets = [sheet.title for sheet in gc.open('Клини богини').worksheets()]
    tables = db.get_table_names()
    for table in db.get_table_names():
        if table in sheets and table != 'Storage':
            sh = gc.open('Клини богини').worksheet(table)
            sh.clear()
        elif table != 'Storage':
            gc.open('Клини богини').add_worksheet(table, 0, 0)
            sh = gc.open('Клини богини').worksheet(table)
        else:
            continue
        cols = db.get_columns(table)
        sh.append_row(cols)
        sh.append_rows(db.get_table(table))
    print('synced')
    time.sleep(600)

# input()