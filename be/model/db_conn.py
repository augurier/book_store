from be.model import store
from fe import conf


class DBConn:
    def __init__(self):
        self.database = store.get_db_conn()
        if conf.Use_Large_DB:
            self.col_book = self.database["book_lx"]
        else:
            self.col_book = self.database["book"]

    def user_id_exist(self, user_id):
        col_user = self.database["user"]
        row = col_user.find_one({'user_id': user_id}, {})
        if row is None:
            return False
        else:
            return True

    def book_id_exist(self, store_id, book_id):
        col_store = self.database["store"]
        row = col_store.find_one({'store_id': store_id, 'books.book_id': book_id}, {})
        if row is None:
            return False
        else:
            return True

    def store_id_exist(self, store_id):
        col_store = self.database["store"]
        row = col_store.find_one({'store_id': store_id}, {})
        if row is None:
            return False
        else:
            return True
