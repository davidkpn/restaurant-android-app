import sqlite3
import time
import os


######## INITIAL ACTIONS##########
def create_tables(con):
    create_products_table_query = """
    CREATE TABLE IF NOT EXISTS products (
    	ID integer PRIMARY KEY AUTOINCREMENT,
    	title text NOT NULL,
      	price real NOT NULL,
      	picture_path text NOT NULL,
        category_id integer NOT NULL
    );
    """

    # order = {products:[ [1,1], [2,1] ], ready:False}
    # products = list[[id,quantity]...]
    create_invoices_table_query = """
    CREATE TABLE IF NOT EXISTS invoices (
    	ID integer PRIMARY KEY AUTOINCREMENT,
    	title text NOT NULL,
      	orders text NOT NULL,
      	total_price real NOT NULL,
      	create_datetime text NOT NULL,
      	is_paid INTEGER NOT NULL,
        session_id INTEGER NOT NULL
    );
    """


    create_categories_table_query = """
    CREATE TABLE IF NOT EXISTS categories (
    	ID integer PRIMARY KEY AUTOINCREMENT,
    	title text NOT NULL,
        picture_path text NOT NULL
    );
    """

    create_sessions_table_query = """
    CREATE TABLE IF NOT EXISTS sessions (
    	ID integer PRIMARY KEY AUTOINCREMENT,
    	time_start text NOT NULL,
        time_end text,
        total_earn integer NOT NULL
    );
    """


    cur = con.cursor()
    cur.execute(create_products_table_query)
    cur.execute(create_invoices_table_query)
    cur.execute(create_categories_table_query)
    cur.execute(create_sessions_table_query)
    con.commit()
    cur.close()



def drop(con, table_name):
    query = f"DROP TABLE IF EXISTS {table_name};"
    cur = con.cursor()
    cur.execute(query)
    con.commit()
    cur.close()


def seed_products(con):
    items = [('Maccabi', 17.5, './assets/maccabi.jpg', 2),
             ('stella', 18.5, './assets/stella.jpg', 2),
             ('Arak Shot', 15, './assets/shot.jpg', 3),
             ('Van Goh Shot', 15, './assets/shot.jpg', 3),
             ('Malabi', 25, './assets/malabi.jpg', 1),
            ]
    cur = con.cursor()
    cur.executemany('INSERT INTO products VALUES (null,?,?,?,?)', items)
    con.commit()
    cur.close()

def seed_invoices(con):
    items = [('table 1', "[{'products':[[0, 1], [1,1], [2,1], [3,2]], 'ready':False}]", 96, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())), 0, 1),
             ('taasdas', "[{'products':[[0, 1], [1,1]], 'ready':False}]", 111, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())), 1, 1),
            ]
    cur = con.cursor()
    cur.executemany('INSERT INTO invoices VALUES (null,?,?,?,?,?,?)', items)
    con.commit()
    cur.close()

def seed_categories(con):
    items = [('Food','./assets/shot.jpg'),
             ('Beers','./assets/shot.jpg'),
             ('Shots','./assets/shot.jpg'),
             ('None-Alc','./assets/shot.jpg')
            ]
    cur = con.cursor()
    cur.executemany('INSERT INTO categories VALUES (null,?,?)', items)
    con.commit()
    cur.close()


def init_db(con):
    drop(con, "invoices")
    drop(con, "products")
    create_tables(con)
    seed_products(con)
    seed_invoices(con)
    seed_categories(con)

"""instead of manipulating every cursor call to dictionary:
#   columns = [col[0] for col in cur.description]
#   data = [dict(zip(columns, row)) for row in cur.fetchall()]
this function will occur on each row on the receiving procces.
"""
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

############DB Class Actions###################
class Api():
    def __init__(self):
        self.__con = con = sqlite3.connect('resturant.db')
        self.__con.row_factory = dict_factory


    def get_all_items(self, table_name):
        cur = self.__con.cursor()
        cur.execute(f'SELECT * FROM {table_name}')
        data = cur.fetchall()
        if table_name == "invoices":
            for row in data:
                row['orders'] = eval(row['orders'])
        cur.close()
        return data

    def get_all_by_exp(self, expression, value, table_name):
        cur = self.__con.cursor()
        cur.execute(f'SELECT * FROM {table_name} WHERE {expression}', (value,))
        data = cur.fetchall()
        if table_name == "invoices":
            for row in data:
                row['orders'] = eval(row['orders'])
        cur.close()
        return data

    """get
    id is ingeter
    table_name is string
    return row => dictionary of the item {"ID": 1, "title": "example"...}
    """
    def get_item_by_id(self, id, table_name):
        cur = self.__con.cursor()
        cur.execute(f'SELECT * FROM {table_name} WHERE ID = {id}')
        row = cur.fetchone()
        if table_name == 'invoices':
            row['orders'] = eval(row['orders'])
        cur.close()
        return row

    """add new item
    item => dictionary of the item {"ID": 1, "title": "example"...}
    table_name is string
    return the item
    """
    def add_item(self, item, table_name):
        cur = self.__con.cursor()
        if table_name == "invoices":
            print(item)
            item['orders'] = str(item['orders'])
            print(len(item) )
        # skip the ID column so the sql will generate a proper ID
        question_str = ','.join('?'*(len(item)-1))
        cur.execute(f"INSERT INTO {table_name} ({','.join(item.keys())}) VALUES (null,{question_str})", tuple(item.values())[1:])
        self.__con.commit()
        item['ID'] = cur.lastrowid
        print(item['ID'])
        cur.close()

        if table_name == "invoices":
            item['orders'] = eval(item['orders'])

        return item

    """update existing item
    item => dictionary of the item {"ID": 1, "title": "example"...}
    table_name is string
    return  ( maybe I should return a success or error message.. for V2)
    """
    def update_item(self, item, table_name):
        cur = self.__con.cursor()
        keys_str = ' = ?,'.join(tuple(item.keys())[1:])
        keys_str += " = ?"
        if table_name == "invoices":
            item['orders'] = str(item['orders'])
        cur.execute(f"UPDATE {table_name} SET {keys_str} WHERE id = ?", (tuple(item.values())[1:]+(item['ID'],)) )
        self.__con.commit()
        cur.close()
        if table_name == "invoices":
            item['orders'] = eval(item['orders'])
        return item

    """delete item from table
    item => dictionary of the item {"ID": 1, "title": "example"...}
    table_name is string
    """
    def delete_item(self, id, table_name):
        cur = self.__con.cursor()
        cur.execute(f'DELETE FROM {table_name} WHERE id=?', (id,))
        self.__con.commit()
        cur.close()

    def close_api_connection(self):
        self.__con.close()
#################################################




if __name__ == '__main__':
    if not os.path.isfile('./resturant.db'):
        con = sqlite3.connect('resturant.db')
        init_db(con)
        con.close()

    api = Api()
    print(api.get_all_items("invoices"))
    print(api.get_all_items("products"))
    print(api.get_all_items("categories"))
