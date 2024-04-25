import logging
import pymongo
import threading
import pymongo.errors as mongo_error



class Store:
    database: str

    def __init__(self, db_path):
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        self.database = myclient["bookstore_db"]
        self.init_tables()

    def init_tables(self):
        try:
            #conn = self.get_db_conn()
            self.database["user"].drop()
            col_user = self.database["user"]
            col_user.create_index([("user_id", 1)], unique=True)
            # conn.execute(
            #     "CREATE TABLE IF NOT EXISTS user ("
            #     "user_id TEXT PRIMARY KEY, password TEXT NOT NULL, "
            #     "balance INTEGER NOT NULL, token TEXT, terminal TEXT);"
            # )
            self.database["user_store"].drop()
            col_user_store = self.database["user_store"]
            col_user_store.create_index([("user_id", 1), ("store_id", 1)], unique=True)
            # conn.execute(
            #     "CREATE TABLE IF NOT EXISTS user_store("
            #     "user_id TEXT, store_id, PRIMARY KEY(user_id, store_id));"
            # )
            self.database["store"].drop()
            col_store = self.database["store"]
            col_store.create_index([("store_id", 1), ("book_id", 1)], unique=True)
            # conn.execute(
            #     "CREATE TABLE IF NOT EXISTS store( "
            #     "store_id TEXT, book_id TEXT, book_info TEXT, stock_level INTEGER,"
            #     " PRIMARY KEY(store_id, book_id))"
            # )
            self.database["new_order"].drop()
            col_new_order = self.database["new_order"]
            col_new_order.create_index([("order_id", 1)], unique=True)
            # conn.execute(
            #     "CREATE TABLE IF NOT EXISTS new_order( "
            #     "order_id TEXT PRIMARY KEY, user_id TEXT, store_id TEXT,"
            #     "state TEXT DEFAULT 'wait for payment',"
            #     "order_datetime TEXT)"
            # )
            self.database["new_order_detail"].drop()
            col_new_order_detail = self.database["new_order_detail"]
            col_new_order_detail.create_index([("order_id", 1), ("book_id", 1)], unique=True)
            # conn.execute(
            #     "CREATE TABLE IF NOT EXISTS new_order_detail( "
            #     "order_id TEXT, book_id TEXT, count INTEGER, price INTEGER,  "
            #     "PRIMARY KEY(order_id, book_id))"
            # )
            self.database["his_order"].drop()
            col_his_order = self.database["his_order"]
            col_his_order.create_index([("order_id", 1)], unique=True)
            # conn.execute(
            #     "CREATE TABLE IF NOT EXISTS history_order( "
            #     "order_id TEXT PRIMARY KEY, user_id TEXT, store_id TEXT, "
            #     "state TEXT DEFAULT 'wait for payment', "
            #     "order_datetime TEXT)"
            # )
            self.database["history_order_detail"].drop()
            self.database["his_order_detail"].drop()
            col_his_order_detail = self.database["his_order_detail"]
            col_his_order_detail.create_index([("order_id", 1), ("book_id", 1)], unique=True)
            # conn.execute(
            #     "CREATE TABLE IF NOT EXISTS history_order_detail( "
            #     "order_id TEXT, book_id TEXT, count INTEGER, price INTEGER,  "
            #     "PRIMARY KEY(order_id, book_id))"
            # )            
            
        except mongo_error.PyMongoError as e:
            logging.error(e)


    def get_db_conn(self):
        return self.database


database_instance: Store = None
# global variable for database sync
init_completed_event = threading.Event()


def init_database(db_path):
    global database_instance
    database_instance = Store(db_path)

#改为返回database（而不是conn）
def get_db_conn():
    global database_instance
    return database_instance.get_db_conn()
