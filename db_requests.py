import json
import sqlite3 as sl
import datetime
from dateutil.relativedelta import relativedelta
with open('config.json') as file:
    db_path = json.load(file)['db_path']
    print('database connected to ' + db_path)
db = sl.connect(db_path, check_same_thread=False)
pending_orders = {}
if __name__ == '__main__':
    # category_list = ['Напитки', 'Курица', 'Мясо', 'Рыба', 'Салаты', 'Алкогольные напитки',
    #                  'Пиццы', 'Соусы', 'Десерты', 'Роллы', 'Детское меню']
    # food_list = [['Кока-кола 0.5л в стекле', 2.50, 0, 1, 5], ['Бонаква 0.5л в стекле', 2.50, 0, 1, 5],
    #              ['Фанта 0.5л в стекле', 2.50, 0, 1, 5], ['Фанта 1л', 3.50, 0, 1, 5],
    #              ['Кока-кола 0.6л в стекле', 2.50, 0, 1, 5], ['Бонаква 0.6л в стекле', 2.50, 0, 1, 5],
    #              ['Фанта 0.6л в стекле', 2.50, 0, 1, 5], ['Фанта 1.1л', 3.50, 0, 1, 5],
    #              ['Кока-кола 0.7л в стекле', 2.50, 0, 1, 5], ['Бонаква 0.7л в стекле', 2.50, 0, 1, 5],
    #              ['Фанта 0.7л в стекле', 2.50, 0, 1, 5], ['Фанта 1.2л', 3.50, 0, 1, 5],
    #              ['Куриные наггетсы 9 шт', 7.99, 0, 2, 20], ['Куриные наггетсы 15 шт', 10.49, 0, 2, 20],
    #              ['Свинные отбивные 350 гр', 7.99, 0, 3, 25], ['Мясо по французски 350 гр', 9.99, 0, 3, 25],
    #              ['Филе хека 300 гр', 9.34, 0, 4, 40], ['Запеченый лосось 500 г', 20.99, 0, 4, 50],
    #              ['Мимоза 350 гр', 6.20, 0, 5, 20], ['Селедь под шубой 350 гр', 7.09, 0, 5, 20],
    #              ['Пиво Stella Artois 350 гр', 5.20, 0, 6, 5], ['Вино Alazan Valley 350 гр', 5.20, 0, 6, 20],
    #              ['Пицца 4 сыра 700 гр', 15.30, 0, 7, 30], ['Пицца маргарита 700 гр', 14.10, 0, 7, 30]]

    with db as con:
        # Orders
        con.execute('''
                    CREATE TABLE IF NOT EXISTS Orders(
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER,
                    time_placed TEXT,
                    is_finished INTEGER,
                    is_aborted INTEGER,
                    total_price REAL,
                    time_required float,
                    date TEXT,
                    time TEXT) 
                    ''')
        con.execute(f'''INSERT INTO Orders (client_id, time_placed, is_finished, is_aborted, total_price, time_required, date, time) VALUES(1, '2024.02.23 5:15', 0, 0, 120.0, 3, '2024.02.24', '9:00')''')
        # Equip_lists
        con.execute('''
                    CREATE TABLE IF NOT EXISTS Equip_lists(
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    equip_id INTEGER,
                    amount float,
                    order_id INTEGER,
                    service_id INTEGER,
                    employee_id)
                    ''')

        # Equip
        con.execute('''
                    CREATE TABLE IF NOT EXISTS Equip(
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    is_consumable INTEGER,
                    is_expire INTEGER,
                    units TEXT)
                    ''')
        Equip_insert = '''INSERT INTO Equip (name, is_consumable, is_expire, units) VALUES (?,?,?,?)'''
        equip = [
            ['Пылесос', 0, 0, 'шт'],
            ['Тряпка', 1, 0, 'шт'],
            ['Моющее средство', 1, 1, 'мл'],
            ['Средство для мытья окон', 1, 1, 'мл'],
            ['Утюг', 0, 0, 0]
        ]
        con.executemany(Equip_insert, equip)
        # for i in food_list:   # fill
        #     con.execute(sql_insert, i)

        # Storage
        con.execute('''
                    CREATE TABLE IF NOT EXISTS Storage(
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    equip_id INTEGER,
                    amount FLOAT,
                    expire_date TEXT
                    )
                    ''')
        Storage_insert = '''INSERT INTO Storage (equip_id, amount, expire_date) VALUES (?,?,?)'''
        storage = [
            [1, 2, ''],
            [2, 100, ''],
            [3, 5000, '16.09.2024'],
            [3, 10000, '05.03.2025'],
            [4, 5000, '05.03.2025'],
        ]
        con.executemany(Storage_insert, storage)

        # Employees
        con.execute('''
                    CREATE TABLE IF NOT EXISTS Employees(
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    tg_id INTEGER,
                    dob TEXT,
                    google_account TEXT)
                    ''')
        employees_insert = '''INSERT INTO Employees (name, tg_id, dob, google_account) VALUES (?,?,?,?)'''
        con.execute(employees_insert, ["Юра", 413844851, '12.12.1998', '  '])
        # con.execute(employees_insert, ["Костя",821927308, 24, 821927308])

        #Employees_lists
        con.execute('''
                    CREATE TABLE IF NOT EXISTS Employees_lists(
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER,
                    employee_id INTEGER)
                    ''')
        employees_list_insert = '''INSERT INTO Employees_lists (order_id, employee_id) VALUES (?,?)'''
        con.execute(employees_list_insert, [1, 1])
        # Clients
        con.execute('''
                    CREATE TABLE IF NOT EXISTS Clients(
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    tg_nickname TEXT,
                    tel INTEGER,
                    adress TEXT,
                    chat_id INTEGER)
                    ''')
        sql_insert = '''INSERT INTO Clients (tg_nickname, tel , adress, chat_id) VALUES (?,?,?,?)'''
        con.execute(sql_insert, ['meme', 375291234567, 'ул. Пушкина д.42 к.2, кв 69', 123456789])
        # Reviews
        con.execute('''
                    CREATE TABLE IF NOT EXISTS Reviews(
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER,
                    rating INTEGER,
                    comment TEXT
                    )
                    ''')
        # Services_lists
        con.execute('''
                    CREATE TABLE IF NOT EXISTS Services_lists(
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    order_id INTEGER,
                    service_id INTEGER,
                    count INTEGER)
                    ''')
        # Services
        con.execute('''
                    CREATE TABLE IF NOT EXISTS Services(
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    price float,
                    time float,
                    is_scaleable INTEGER)
                    ''')
        services_insert = '''INSERT INTO Services (name, price, time, is_scaleable) VALUES (?,?,?,?)'''
        services = [
                    ['Базовая цена', 31, 1.5, 0],
                    ['Комната', 14, 1, 1],
                    ['Санузел', 20, 0.5, 1],
                    ['Внутри холодильника', 25, 1, 0],
                    ['Внутри духовки', 25, 1, 0],
                    ['Внутри кухонных шкафов', 25, 1, 0],
                    ['Помоем посуду', 10, 0.5, 0],
                    ['Внутри микроволновки', 20, 0.5, 0],
                    ['Погладим белье', 20, 1, 1],
                    ['Помоем окна', 15, 0.5, 1],
                    ['Уберем на балконе', 20, 1, 1]
                    ]
        con.executemany(services_insert, services)

        # Service_req
        con.execute('''
                    CREATE TABLE IF NOT EXISTS Service_req(
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    equip_id INTEGER,
                    amount float,
                    service_id INTEGER)
                    ''')
        service_req_insert = '''INSERT INTO Service_req (equip_id, amount, service_id) VALUES (?,?,?)'''
        service_reqs = [
            [1, 1, 1],
            [2, 3, 1],
            [2, 3, 2],
            [3, 100, 1],
            [3, 100, 2],
            [3, 100, 3],
            [5, 1, 9]
        ]
        con.executemany(service_req_insert, service_reqs)

# further below there will be the most common requests
# to make it easier to implement this to bots


class DataBase:
    def __init__(self):
        global db
        self.db = db

    def get_services(self, all=False):

        """
        :param all: if False excludes base_price, room and bath

        Returns dict of all services {name: {id: x, price:y, time:z(in hours), is_scaleable:(1 or 0)}}
        """
        if not all:
            base_filter = " WHERE name NOT IN ('Базовая цена','Комната','Санузел')"
        else:
            base_filter = ""
        with self.db as con:
            services = con.execute(f'''SELECT * FROM Services {base_filter}''').fetchall()
            services_dict = {}
            for i in services:
                services_dict[i[1]] = {'id': i[0],
                                      'price': i[2],
                                      'time': i[3],
                                      'is_scaleable': i[4]
                                       }
            return services_dict

    def get_columns(self, name: str) -> list:
        """
        get all column names
        :param name: table name as string, as example 'Goods'
        """
        with self.db as con:
            result = con.execute(f'''select * from pragma_table_info('{name}')''').fetchall()
            return [i[1] for i in result]

    def get_storage(self, exp=False, names=False):
        """
        Returns dict of items_names and amount {name: price, ...}
        """
        with self.db as con:
            exp_check = ''
            if exp:
                exp_check = ', expire_date'
            if names:
                items = con.execute(f'''
                                    SELECT name, SUM(amount){exp_check}, units FROM Storage
                                    JOIN Equip ON Equip.id = Storage.equip_id
                                    GROUP BY name{exp_check}
                                    ''').fetchall()
                return items
            else:

                items = con.execute(f'''
                                                    SELECT equip_id, SUM(amount){exp_check} FROM Storage
                                                    GROUP BY equip_id
                                                    ''').fetchall()
                dict_of_storage = {}
            for i in items:
                dict_of_storage[i[0]] = i[1]
            return dict_of_storage

    def get_table(self,name):
        with self.db as con:
            return con.execute(f'''SELECT * FROM {name}''').fetchall()

    def get_equip_req(self, services_dict, date):
        req_equip_dict = {}    # db.get_equip_req({"Базовая цена":1, "Комната":1, "Санузел": 1})
        with self.db as con:
            sql_srvcs_lst = ','.join(f"\'{service}\'" for service in services_dict.keys())
            db_srv_dict = db.get_services(all=True)
            for key in services_dict.keys():
                services_dict[key] = {'amount': services_dict[key]['amount'],
                                      'id': db_srv_dict[key]['id']}
            for key in services_dict:
                services_dict[key]['req'] = {}
                srv_id = services_dict[key]['id']
                single_service_req = con.execute(f'''Select equip_id, amount, is_consumable FROM Service_req 
                                                     JOIN Equip ON Equip.id = Service_req.equip_id
                                                     WHERE service_id = {srv_id}''').fetchall()
                for item in single_service_req:                                                     # do not multiply for not consumable
                    services_dict[key]['req'][item[0]] = item[1] * (services_dict[key]['amount'] ** int(bool(item[2])))
                    if item[0] in req_equip_dict:
                        req_equip_dict[item[0]] += item[1] * (services_dict[key]['amount'] ** int(bool(item[2])))
                    else:
                        req_equip_dict[item[0]] = item[1] * (services_dict[key]['amount'] ** int(bool(item[2])))
            storage = db.get_storage()
            print(storage)
            if datetime.date(int(date.split('.')[0]), int(date.split('.')[1]), int(date.split('.')[2])) <= datetime.date.today() + relativedelta(weeks=1):
                for key in req_equip_dict:
                    print('req_equip_dict:    ', req_equip_dict)
                    print('storage:    ', storage)
                    if key in storage:
                        if req_equip_dict[key] > storage[key]:
                            print('none 1')
                            return None
                    else:
                        print('none 2')
                        return None

                    print(req_equip_dict)
                    return req_equip_dict

            else:
                print(req_equip_dict)
                return req_equip_dict

    def get_schedule(self, date, employee_id):
        with self.db as con:
            schedule = con.execute(f'''SELECT time, time_required FROM Employees
                           JOIN Employees_lists ON Employees.id = Employees_lists.employee_id
                           JOIN Orders ON Orders.id = Employees_lists.order_id
                           WHERE date == '{date}' ''').fetchall()
        return schedule

    def get_availiable_employees(self, n_employees, date, order_time):
        with self.db as con:
            order_time += 0.5
            e_ids = con.execute('''SElECT id FROM Employees''').fetchall()
            availiable_employees = {}
            sum_time_pool = []
            if n_employees == 1:
                for e_id in e_ids:
                    time_limit = 10
                    min_time = 18
                    if str(datetime.date.today()).replace('-','.') == date:
                        min_time = int((int(str(datetime.datetime.now().time()).split(':')[0]) + 1.5 + int(int(str(datetime.datetime.now().time()).split(':')[1]) > 30))*2)
                    time_pool = [i for i in range(min_time, 37)]
                    schedule = self.get_schedule(date, e_id[0])
                    for order in schedule:  # order[0] is time ;   order[1] is time-required
                        time_limit -= order[1]
                        t = int(order[0].split(':')[0]) + int(order[0].split(':')[1] == '30') * 0.5
                        for i in range(int(t*2), int(2*(t+order[1]))):
                            if i in time_pool:
                                time_pool.remove(i)
                    # if > 10 hours
                    if time_limit < order_time:
                        continue
                    for h in time_pool:
                        if h+order_time*2 <= 36:
                            if (h+int(order_time*2) not in time_pool) or (h+int(order_time) not in time_pool) or h + int(order_time*2) >= 48:
                                time_pool.remove(h)
                    if time_pool:
                        availiable_employees[e_id[0]] = time_pool

                for key in availiable_employees:
                    for time in availiable_employees[key]:
                        if time not in sum_time_pool:
                            sum_time_pool.append(time)

            else:  # multiple eployees
                return None  # under_construction

            if sum_time_pool:
                return sum_time_pool, availiable_employees
            else:
                return None

    def get_time_availiable(self, date: str, order_time, services_dict):
        """        # -s !!!!!
        Seeks ranges of availiable time at given date
        :param date: YYYY.MM.DD
        :param order_time: time in hours
        :param services_dict: {service_name: quantity}
        :return:
        """
        time_ranges = []
        with self.db as con:
            # number of employeers required
            if order_time > 100: # later
                n_employees = order_time//10 + 1
                t = order_time/n_employees
                employees = self.get_availiable_employees(n_employees, date, t)
            else:
                n_employees = 1
                employees = self.get_availiable_employees(n_employees, date, order_time)
            equip = self.get_equip_req(services_dict, date)
            # equip check on employee
            # if date != str(datetime.date.today()).replace('-', '.'):
            #     # e_flag,  equip check on employee request
            #     # e_list = {}
            # else:
            #     equip = self.get_equip_req(services_dict)

            if employees and equip:
                return employees[0], employees[1], equip
            else:
                return None


    def insert_order(self, client_tg_id, order_info:dict):
        # need to add 30 min to time req
        order_info['duration'] += 0.5
        """
        Inserts order and order list(shopping cart) to the database.
        time_placed is "DD.MM.YYYY HH:MM".

        :param order_list: dict {'name': 'amount', ...}
        :return: delivery time in minutes
        :rtype: int
        """
        with self.db as con:
            # select or add client
            client_id = con.execute('''SELECT id FROM orders''').fetchone()[0]
            if not client_id:
                client_id = self.insert_client('', order_info['tel'], order_info['adress'], client_tg_id)
            now = str(datetime.datetime.now())
            current_datetime = now.split(' ')[0].replace('-', '.') + ' ' + now.split(' ')[1][:5]
            # add order with blank client_id(if there is no such in db) and total price
            print(client_id)
            print(current_datetime)
            print(order_info)
            con.execute(f'''INSERT INTO Orders (client_id, time_placed,
                                                      is_finished, is_aborted,
                                                      total_price,
                                                      time_required,
                                                      date, time)
                                  VALUES ({client_id},'{current_datetime}',0,0,{order_info['total_sum']},{order_info['duration']},'{order_info['date']}', '{order_info['time']}') ''')

            order_id = con.execute('SELECT max(id)  from Orders').fetchone()[0]
            print(con.execute('SELECT * FROM Orders').fetchall())

            # insert services_lists (select form services where name in (serivces_dict.keys())
            for key in order_info['services_dict']:
                con.execute(f'''INSERT INTO Services_lists (order_id, service_id, count) 
                                VALUES({order_id},{con.execute(f"SELECT id FROM Services WHERE name ='{key}'").fetchone()[0]}, {order_info['services_dict'][key]['amount']} )''')

            # insert to Employees_lists (select max order_id), (select employee_id by employee_tg_id)
            con.execute(f'''INSERT INTO Employees_lists (order_id, employee_id) 
                                            VALUES({order_id}, {db.get_employee_id(order_info['employee'])[0]})''')


    def get_employee_id(self, tg_id):
        with self.db as con:
            return con.execute(f'''SELECT id,name FROM Employees
                                       WHERE tg_id = '{tg_id}'
                                       ''').fetchone()

    def get_client(self, client_chat_id: int):
        """
         Returns tuple of client data or None if there is no such.

        :return: (id, name, tel, age, adress, chat_type, chat_id) or None
        :param client_chat_id: id of client chat
        :rtype: tuple
        """
        with self.db as con:
            client = con.execute(f'''
                           SELECT * from Clients
                           WHERE chat_id = {client_chat_id}
            ''')
            client = client.fetchone()
            if client:
                return client
            else:
                return None

    def insert_client(self, tg_nickname: str, tel: int, adress: str, chat_id: int):
        """
        If client in database - retruns id, if not - adds and return id

        :return: id of inserted client
        :rtype: int
        """
        with self.db as con:
            client_args = {'tg_nickname': tg_nickname,
                           'tel': tel,
                           'adress:': adress,
                           'chat_id': chat_id}
            a = con.execute(f'''
                                   SELECT * from Clients
                                   WHERE chat_id = {chat_id}
                    ''').fetchone()
            if a == client_args:
                client_id = a[0]
            elif a:
                for param, client_arg, db_val in client_args.items(), a:
                    if client_arg != db_val:
                        self.update_cell('Clients', a[0], param, client_arg)
            else:
                con.execute(f'''INSERT INTO Clients (name, tel, adress, chat_id)
                                  VALUES ('{tg_nickname}', {tel}, '{adress}', {chat_id}) ''')
                client_id = con.execute('''SELECT max(id) FROM Clients''').fetchone()[0]
            return client_id

    def insert_employee(self, name: str, tg_id: int, google_account: str, dob: str):
        """
        Inserts employee to database

        """
        with self.db as con:
            a = con.execute(f'''
                                   SELECT * from Admins
                                   WHERE tg_id = {tg_id}
                    ''').fetchone()
            if a:
                tg_id = a[0][2]
            else:
                con.execute(f'''INSERT INTO Employees (name, tg_id, google_account, dob)
                                  VALUES ('{name}', {tg_id}, {google_account}, {dob}''')

    def del_employee(self, tg_id):
        with self.db as con:
            con.execute(f'''DELETE FROM Employees
                            WHERE tg_id = {tg_id}''')

    # def stop_food(self, food_name):
    #     with self.db as con:
    #         con.execute(f'''UPDATE Food
    #                         SET stop_flag = 1
    #                         WHERE name = '{food_name}' ''')

    # def unstop_food(self, food_name):
    #     with self.db as con:
    #         con.execute(f'''UPDATE Food
    #                         SET stop_flag = 0
    #                         WHERE name = '{food_name}' ''')

    # def get_item(self, table: str,  value: any, by='id'):
    #     """
    #     Returns record from table by any given field (by id as default)
    #
    #     :rtype: tuple
    #     """
    #     if type(value) == str:
    #         value = "'"+value+"'"
    #     with self.db as con:
    #         return con.execute(f'''SELECT * FROM {table}
    #                         WHERE {by} = {value}''').fetchall()

    def update_cell(self, table: str, id: int, param: str, value: any):
        """
        Sets parameter(param) of item(by id) in table(table) to (value)
        """
        if type(value) == str:
            value = "'"+value+"'"
        with self.db as con:
            con.execute(f'''UPDATE {table}
                            SET '{param}' = {value}
                            WHERE id = {id} ''')

    def del_item(self, table: str, id: int):
        """
        Deletes record from table by id
        """
        with self.db as con:
            con.execute(f'''DELETE FROM {table}
                            WHERE id = {id}''')

    def get_equip(self):
        """
        Returns dict of equip availiable at the moment from storage {name:amount}
        """
        with self.db as con:
            con.execute(f'''SELECT name FROM Equip
                            JOIN 
                            ''')


    # statistics daily
    # def day_stat(self, date):
    #     day, month, year = date.split('.')
    #     with self.db as con:
    #         count = con.execute(f"""SELECT COUNT(id) FROM Orders
    #                                 WHERE time_placed LIKE '{day}.{month}.{year}%'
    #                                 """).fetchone()[0]
    #         delivered = con.execute(f"""SELECT COUNT(id) FROM Orders
    #                                     WHERE time_placed LIKE '{day}.{month}.{year}%' AND
    #                                           is_finished = 1
    #                                 """).fetchone()[0]
    #         aborted = con.execute(f"""SELECT COUNT(id) FROM Orders
    #                                     WHERE time_placed LIKE '{day}.{month}.{year}%' AND
    #                                           is_aborted = 1
    #                                 """).fetchone()[0]
    #     return f"Ordered at this day:{count}\nDelivered at this day:{delivered}\nAborted orders at this day:{aborted}"

    # statistics weekly
    # def week_stat(self, date):
    #     day, month, year = date.split('.')
    #     week = dt.date(int(year), int(month), int(day)).isocalendar().week
    #     week = [dt.date.fromisocalendar(int(year), week, i) for i in range(1, 8)]
    #     dates = [f'{i.day}.{i.month}.{i.year}' for i in week]
    #     cond_list = ''
    #     for i in dates:
    #         cond_list += f"time_placed LIKE '{i.split('.')[0]}.{i.split('.')[1]}.{i.split('.')[2]}%' AND "
    #     cond_list = cond_list[:-5]
    #     with self.db as con:
    #             count = con.execute(f"""SELECT COUNT(id) FROM Orders
    #                                                WHERE time_placed LIKE {cond_list}
    #                                                """).fetchone()[0]
    #             delivered = con.execute(f"""SELECT COUNT(id) FROM Orders
    #                                                    WHERE time_placed LIKE {cond_list} AND
    #                                                          is_finished = 1
    #                                                """).fetchone()[0]
    #             aborted = con.execute(f"""SELECT COUNT(id) FROM Orders
    #                                                    WHERE time_placed LIKE {cond_list} AND
    #                                                          is_aborted = 1
    #                                                """).fetchone()[0]
    #     return f"Ordered at this week:{count}\nDelivered at this week:{delivered}\nAborted orders at this week:{aborted}"


db = DataBase()