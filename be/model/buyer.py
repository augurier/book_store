import sqlite3 as sqlite
import uuid
import json
import logging
from be.model import db_conn
from be.model import error
import time


class Buyer(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def new_order(
        self, user_id: str, store_id: str, id_and_count: tuple[(str, int)]
    ) -> tuple[(int, str, str)]:
        order_id = ""
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id,)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + (order_id,)
            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))

            for book_id, count in id_and_count:
                cursor = self.conn.execute(
                    "SELECT book_id, stock_level, book_info FROM store "
                    "WHERE store_id = ? AND book_id = ?;",
                    (store_id, book_id),
                )
                row = cursor.fetchone()
                if row is None:
                    return error.error_non_exist_book_id(book_id) + (order_id,)

                stock_level = row[1]
                book_info = row[2]
                book_info_json = json.loads(book_info)
                price = book_info_json.get("price")

                if stock_level < count:
                    return error.error_stock_level_low(book_id) + (order_id,)

                cursor = self.conn.execute(
                    "UPDATE store set stock_level = stock_level - ? "
                    "WHERE store_id = ? and book_id = ? and stock_level >= ?; ",
                    (count, store_id, book_id, count),
                )
                if cursor.rowcount == 0:
                    return error.error_stock_level_low(book_id) + (order_id,)

                self.conn.execute(
                    "INSERT INTO new_order_detail(order_id, book_id, count, price) "
                    "VALUES(?, ?, ?, ?);",
                    (uid, book_id, count, price),
                )

            # cur_time = time.strftime("%Y-%m-%d %H:%M:%S")
            cur_time=str(int(time.time())) #纪元以来的秒数
            self.conn.execute(
                "INSERT INTO new_order(order_id, store_id, user_id,state,order_datetime) "
                "VALUES(?, ?, ?, ?, ?);",
                (uid, store_id, user_id, "wait for payment", cur_time),
            )
            self.conn.commit()
            order_id = uid
        except sqlite.Error as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""

        return 200, "ok", order_id

    #调用之前需要调用者保证order_id合法
    def order_timeout(self,order_id:str) -> tuple[(int,str)]:
        conn=self.conn
        try:
            cursor=conn.execute("INSERT INTO history_order SELECT * FROM new_order WHERE order_id=?",
                                (order_id,))
            cursor=conn.execute("UPDATE history_order SET state = 'cancelled' "
                                "WHERE state='wait for payment' AND order_id=?",
                                (order_id,))
            cursor=conn.execute("DELETE FROM new_order WHERE order_id=?",
                                (order_id,))
            
            cursor=conn.execute("INSERT INTO history_order_detail SELECT * FROM new_order_detail "
                                "WHERE order_id=?",
                                (order_id,))
            cursor=conn.execute("DELETE FROM new_order_detail WHERE order_id=?",
                                (order_id,))

        except sqlite.Error as e:
            logging.error(str(e))
            return 528, "{}".format(str(e))

        except BaseException as e:
            return 530, "{}".format(str(e))
        return error.error_order_timeout(order_id)

    def payment(self, user_id: str, password: str, order_id: str) -> tuple[int, str]:
        conn = self.conn
        try:
            cursor = conn.execute(
                "SELECT order_id, user_id, store_id,order_datetime FROM new_order WHERE order_id = ?",
                (order_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return error.error_invalid_order_id(order_id)

            order_id = row[0]
            buyer_id = row[1]
            store_id = row[2]
            order_datetime=int(row[3])
            if buyer_id != user_id:
                return error.error_authorization_fail()
            
            timeout_limit=1 #这里的超时时间设置为1秒，方便调试
            if order_datetime+timeout_limit<int(time.time()):
                return self.order_timeout(order_id)

            cursor = conn.execute(
                "SELECT balance, password FROM user WHERE user_id = ?;", (buyer_id,)
            )
            row = cursor.fetchone()
            if row is None:
                return error.error_non_exist_user_id(buyer_id)
            balance = row[0]
            if password != row[1]:
                return error.error_authorization_fail()

            cursor = conn.execute(
                "SELECT store_id, user_id FROM user_store WHERE store_id = ?;",
                (store_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return error.error_non_exist_store_id(store_id)

            seller_id = row[1]

            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)

            cursor = conn.execute(
                "SELECT book_id, count, price FROM new_order_detail WHERE order_id = ?;",
                (order_id,),
            )
            total_price = 0
            for row in cursor:
                count = row[1]
                price = row[2]
                total_price = total_price + price * count

            if balance < total_price:
                return error.error_not_sufficient_funds(order_id)

            cursor = conn.execute(
                "UPDATE user set balance = balance - ? "
                "WHERE user_id = ? AND balance >= ?",
                (total_price, buyer_id, total_price),
            )
            if cursor.rowcount == 0:
                return error.error_not_sufficient_funds(order_id)

            cursor = conn.execute(
                "UPDATE user set balance = balance + ?" "WHERE user_id = ?",
                (total_price, seller_id),
            )

            if cursor.rowcount == 0:
                return error.error_non_exist_user_id(seller_id)

            # order从new_order中删除并插入history_order中
            cursor = conn.execute(
                "INSERT INTO history_order "
                "SELECT * FROM new_order WHERE order_id=?",
                (order_id,),
            )
            # 更新state为等待发货
            cursor = conn.execute(
                "UPDATE history_order "
                "SET state='wait for delivery' "
                "WHERE order_id=?",
                (order_id,),
            )
            if cursor.rowcount == 0:
                return error.error_invalid_order_id(order_id)
            cursor = conn.execute(
                "DELETE FROM new_order WHERE order_id = ?", (order_id,)
            )
            if cursor.rowcount == 0:
                return error.error_invalid_order_id(order_id)

            # order_detail从new_order_detail中删除并插入history_order_detail中
            cursor = conn.execute(
                "INSERT INTO history_order_detail "
                "SELECT * FROM new_order_detail WHERE order_id=?",
                (order_id,),
            )
            conn.commit()
            cursor = conn.execute(
                "DELETE FROM new_order_detail where order_id = ?", (order_id,)
            )
            if cursor.rowcount == 0:
                return error.error_invalid_order_id(order_id)

            conn.commit()

        except sqlite.Error as e:
            logging.error(str(e))
            return 528, "{}".format(str(e))

        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def add_funds(self, user_id, password, add_value) -> tuple[int, str]:
        try:
            cursor = self.conn.execute(
                "SELECT password from user where user_id=?", (user_id,)
            )
            row = cursor.fetchone()
            if row is None:
                return error.error_authorization_fail()

            if row[0] != password:
                return error.error_authorization_fail()

            cursor = self.conn.execute(
                "UPDATE user SET balance = balance + ? WHERE user_id = ?",
                (add_value, user_id),
            )
            if cursor.rowcount == 0:
                return error.error_non_exist_user_id(user_id)

            self.conn.commit()
        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def cancel_order(
        self, user_id: str, order_id: str
    ) -> tuple[int, str]:
        conn = self.conn
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            #修改state状态，并将其从new_order移到history_order
            cursor = conn.execute(
                "UPDATE new_order set state='cancelled' "
                "WHERE user_id=? AND order_id=? AND state='wait for payment'",
                (user_id,order_id)
            )
            if cursor.rowcount==0:
                return error.error_invalid_order_id(order_id)
            
            cursor=conn.execute(
                "INSERT INTO history_order "
                "SELECT * FROM new_order WHERE order_id=?",
                (order_id,)
            )
            cursor=conn.execute(
                "DELETE FROM new_order "
                "WHERE order_id=?",
                (order_id,)
            )
            if cursor.rowcount==0:
                return error.error_invalid_order_id(order_id)
            
            #将new_order_detail做出相应的改动
            cursor=conn.execute(
                "INSERT INTO history_order_detail "
                "SELECT * FROM new_order_detail WHERE order_id=?",
                (order_id,)
            )
            cursor=conn.execute(
                "DELETE FROM new_order_detail "
                "WHERE order_id=?",
                (order_id,)
            )
            if cursor.rowcount==0:
                return error.error_invalid_order_id(order_id)

            conn.commit()
        except sqlite.Error as e:
            logging.error(str(e))
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200,"ok"

    def receive(self, user_id: str, order_id: str) -> tuple[(int,str)]:
        conn = self.conn
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)

            cursor=conn.execute(
                "UPDATE history_order SET state='received' "
                "WHERE user_id=? AND order_id=? AND state='delivering'",
                (user_id,order_id)
            )
            if cursor.rowcount==0:
                return error.error_invalid_order_id(order_id)

            conn.commit()
        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200,"ok"
    
    #如果store_id是空字符串，则为全站搜索，否则是特定store搜索
    def search(self,keyword:str,content:str,store_id:str) -> tuple[(int,str,list[str])]:
        conn = self.conn
        book_conn=self.book_conn
        try:
            sql = """select distinct book_id from store """
            if not store_id=="":
                sql+=" where store_id={}".format(store_id)
                if not self.store_id_exist(store_id):
                    return error.error_non_exist_store_id(store_id)
            cursor=conn.execute(sql)
            if cursor.rowcount == 0:
                return 200,"ok",[]
            
            bids:tuple[str,]=tuple(map(lambda x:x[0],cursor.fetchall()))
            search_sql="""select id from book 
                where id in {} and {} like '%{}%'""".format(bids,keyword,content)
            cursor=book_conn.execute(search_sql)
            if cursor.rowcount==0:
                return 200,"ok",[]
            res=list(map(lambda x:x[0],cursor.fetchall()))
            conn.commit()
        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200,"ok",res
