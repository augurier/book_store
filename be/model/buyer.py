import pymongo.errors as mongo_error
import uuid
import json
import logging
from be.model import db_conn
from be.model import error


class Buyer(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def new_order(
        self, user_id: str, store_id: str, id_and_count: [(str, int)]
    ) -> (int, str, str):
        order_id = ""
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id,)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + (order_id,)
            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))

            col_store = self.database['store']
            col_new_order_detail = self.database['new_order_detail']
            col_new_order = self.database['new_order']

            
            for book_id, count in id_and_count:
                row = col_store.find_one({'store_id': store_id, 'book_id': book_id},
                                     {'_id': 0, 'book_id': 1, 'stock_level': 1, 'book_info': 1})
                # cursor = self.conn.execute(
                #     "SELECT book_id, stock_level, book_info FROM store "
                #     "WHERE store_id = ? AND book_id = ?;",
                #     (store_id, book_id),
                # )
                # row = cursor.fetchone()
                if row is None:
                    return error.error_non_exist_book_id(book_id) + (order_id,)

                stock_level = row['stock_level']
                book_info = row['book_info']
                book_info_json = json.loads(book_info)
                price = book_info_json.get("price")

                if stock_level < count:
                    return error.error_stock_level_low(book_id) + (order_id,)
                
                rows = col_store.update_one({'store_id': store_id, 'book_id': book_id, 'stock_level': {'$gte': count}}, 
                                           {'$inc': {'stock_level': -1}})

                # cursor = self.conn.execute(
                #     "UPDATE store set stock_level = stock_level - ? "
                #     "WHERE store_id = ? and book_id = ? and stock_level >= ?; ",
                #     (count, store_id, book_id, count),
                # )
                if rows.matched_count != 1:
                    return error.error_stock_level_low(book_id) + (order_id,)

                detail1 = {
                        'order_id' : uid,
                        'book_id' : book_id,
                        'count' : count,
                        'price' : price
                    }
                col_new_order_detail.insert_one(detail1)
                
                # self.conn.execute(
                #     "INSERT INTO new_order_detail(order_id, book_id, count, price) "
                #     "VALUES(?, ?, ?, ?);",
                #     (uid, book_id, count, price),
                # )

            order1 = {
                        'order_id' : uid,
                        'store_id' : store_id,
                        'user_id' : user_id
                    }
            col_new_order.insert_one(order1)
            # self.conn.execute(
            #     "INSERT INTO new_order(order_id, store_id, user_id) "
            #     "VALUES(?, ?, ?);",
            #     (uid, store_id, user_id),
            # )

            order_id = uid
            
          
        except mongo_error.PyMongoError as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""  

        return 200, "ok", order_id

    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        try:
            col_new_order = self.database["new_order"]
            row = col_new_order.find_one({'order_id': order_id}, {'_id': 0, 'order_id': 1, 'user_id': 1, 'store_id': 1})
            # cursor = conn.execute(
            #     "SELECT order_id, user_id, store_id FROM new_order WHERE order_id = ?",
            #     (order_id,),
            # )
            if row is None:
                return error.error_invalid_order_id(order_id)

            order_id = row['order_id']
            buyer_id = row['user_id']
            store_id = row['store_id']

            if buyer_id != user_id:
                return error.error_authorization_fail()

            col_user = self.database["user"]
            row = col_user.find_one({'user_id': buyer_id}, {'_id': 0, 'balance': 1, 'password': 1})
            # cursor = conn.execute(
            #     "SELECT balance, password FROM user WHERE user_id = ?;", (buyer_id,)
            # )

            if row is None:
                return error.error_non_exist_user_id(buyer_id)
            balance = row['balance']
            if password != row['password']:
                return error.error_authorization_fail()

            col_user_store = self.database["user_store"]
            row = col_user_store.find_one({'store_id': store_id}, {'_id': 0, 'store_id': 1, 'user_id': 1})
            # cursor = conn.execute(
            #     "SELECT store_id, user_id FROM user_store WHERE store_id = ?;",
            #     (store_id,),
            # )
            if row is None:
                return error.error_non_exist_store_id(store_id)

            seller_id = row['user_id']

            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)

            col_new_order_detail = self.database["new_order_detail"]
            rows = col_new_order_detail.find({'order_id': order_id}, {'_id': 0, 'book_id': 1, 'count': 1, 'price': 1})
            # cursor = conn.execute(
            #     "SELECT book_id, count, price FROM new_order_detail WHERE order_id = ?;",
            #     (order_id,),
            # )
            total_price = 0
            for row in rows:
                count = row['count']
                price = row['price']
                total_price = total_price + price * count

            if balance < total_price:
                return error.error_not_sufficient_funds(order_id)

            rows = col_user.update_one({'user_id': buyer_id, 'balance': {'$gte': total_price}}, 
                                           {'$inc': {'balance': total_price}})
            # cursor = conn.execute(
            #     "UPDATE user set balance = balance - ?"
            #     "WHERE user_id = ? AND balance >= ?",
            #     (total_price, buyer_id, total_price),
            # )
            if rows.matched_count != 1:
                return error.error_not_sufficient_funds(order_id)
            
            rows = col_user.update_one({'user_id': seller_id}, {'$inc': {'balance': total_price}})
            # cursor = conn.execute(
            #     "UPDATE user set balance = balance + ?" "WHERE user_id = ?",
            #     (total_price, seller_id),
            #)
            if rows.matched_count != 1:
                return error.error_non_exist_user_id(seller_id)

            rows = col_new_order.delete_many({'order_id': order_id})
            # cursor = conn.execute(
            #     "DELETE FROM new_order WHERE order_id = ?", (order_id,)
            # )
            if rows.deleted_count == 0:
                return error.error_invalid_order_id(order_id)

            rows = col_new_order_detail.delete_many({'order_id': order_id})
            # cursor = conn.execute(
            #     "DELETE FROM new_order_detail where order_id = ?", (order_id,)
            # )
            if rows.deleted_count == 0:
                return error.error_invalid_order_id(order_id)

        except mongo_error.PyMongoError as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))


        return 200, "ok"

    def add_funds(self, user_id, password, add_value) -> (int, str):
        try:
            col_user = self.database["user"]
            row = col_user.find_one({'user_id': user_id}, {'_id': 0, 'password': 1})
            # cursor = self.conn.execute(
            #     "SELECT password  from user where user_id=?", (user_id,)
            # )
            if row is None:
                return error.error_authorization_fail()

            if row['password'] != password:
                return error.error_authorization_fail()

            rows = col_user.update_one({'user_id': user_id}, {'$inc': {'balance': add_value}})
            # cursor = self.conn.execute(
            #     "UPDATE user SET balance = balance + ? WHERE user_id = ?",
            #     (add_value, user_id),
            # )
            if rows.matched_count != 1:
                return error.error_non_exist_user_id(user_id)
            
        except mongo_error.PyMongoError as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))


        return 200, "ok"
