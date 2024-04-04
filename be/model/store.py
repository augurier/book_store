import logging
import os
import sqlite3 as sqlite
import threading

class Store:
    database: str

    def __init__(self, db_path):
        self.database = os.path.join(db_path, "be.db")
        self.book_db=os.path.join(db_path,"book.db")
        # logging.error(os.path.dirname(__file__))
        self.init_tables()

    def init_tables(self):
        try:
            conn , book_conn= self.get_db_conn()

            conn.execute("""DROP TABLE IF EXISTS user""")

            conn.execute("""DROP TABLE IF EXISTS user_store""")

            conn.execute("""DROP TABLE IF EXISTS store""")

            conn.execute("""DROP TABLE IF EXISTS new_order""")

            conn.execute("""DROP TABLE IF EXISTS new_order_detail""")

            conn.execute("""DROP TABLE IF EXISTS history_order""")

            conn.execute("""DROP TABLE IF EXISTS history_order_detail""")

            # conn.execute("DROP TABLE IF EXISTS book")

            conn.execute(
                "CREATE TABLE IF NOT EXISTS user ("
                "user_id TEXT PRIMARY KEY, password TEXT NOT NULL, "
                "balance INTEGER NOT NULL, token TEXT, terminal TEXT);"
            )

            conn.execute(
                "CREATE TABLE IF NOT EXISTS user_store("
                "user_id TEXT, store_id, PRIMARY KEY(user_id, store_id));"
            )

            conn.execute(
                "CREATE TABLE IF NOT EXISTS store( "
                "store_id TEXT, book_id TEXT, book_info TEXT, stock_level INTEGER,"
                " PRIMARY KEY(store_id, book_id))"
            )

            conn.execute(
                "CREATE TABLE IF NOT EXISTS new_order( "
                "order_id TEXT PRIMARY KEY, user_id TEXT, store_id TEXT,"
                "state TEXT DEFAULT 'wait for payment',"
                "order_datetime TEXT)"
            )

            conn.execute(
                "CREATE TABLE IF NOT EXISTS new_order_detail( "
                "order_id TEXT, book_id TEXT, count INTEGER, price INTEGER,  "
                "PRIMARY KEY(order_id, book_id))"
            )

            conn.execute(
                "CREATE TABLE IF NOT EXISTS history_order( "
                "order_id TEXT PRIMARY KEY, user_id TEXT, store_id TEXT, "
                "state TEXT DEFAULT 'wait for payment', "
                "order_datetime TEXT)"
            )

            conn.execute(
                "CREATE TABLE IF NOT EXISTS history_order_detail( "
                "order_id TEXT, book_id TEXT, count INTEGER, price INTEGER,  "
                "PRIMARY KEY(order_id, book_id))"
            )

            # conn.execute(
            #     """
            #     CREATE TABLE IF NOT EXISTS book (
            #         id TEXT PRIMARY KEY,
            #         title TEXT,
            #         author TEXT,
            #         publisher TEXT,
            #         original_title TEXT,
            #         translator TEXT,
            #         pub_year TEXT,
            #         pages INTEGER,
            #         price INTEGER,
            #         currency_unit TEXT,
            #         binding TEXT,
            #         isbn TEXT,
            #         author_intro TEXT,
            #         book_intro TEXT,
            #         content TEXT,
            #         tags TEXT,
            #         picture BLOB                   
            #     )
            #     """
            # )

            conn.commit()
        except sqlite.Error as e:
            logging.error(e)
            conn.rollback()

    def get_db_conn(self) -> tuple[(sqlite.Connection,sqlite.Connection)]:
        return sqlite.connect(self.database),sqlite.connect(self.book_db)


database_instance: Store = None
# global variable for database sync
init_completed_event = threading.Event()


def init_database(db_path):
    global database_instance
    database_instance = Store(db_path)


def get_db_conn():
    global database_instance
    return database_instance.get_db_conn()
