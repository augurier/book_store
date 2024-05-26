import uuid
import json
import logging
import pymongo.errors as mongo_error
import psycopg2
from be.model import db_conn
from be.model import error
import time

SEARCH_PAGE_LENGTH = 5

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
            
            cur_time=str(int(time.time())) #纪元以来的秒数
            self.conn.execute(
                "INSERT INTO new_order(order_id, store_id, user_id, state, order_datetime) "
                "VALUES(%s, %s, %s, %s, %s);",
                (uid, store_id, user_id, "wait for payment", cur_time),
            )
            for book_id, count in id_and_count:
                self.conn.execute(
                    "SELECT book_id, stock_level, book_info FROM store "
                    "WHERE store_id = %s AND book_id = %s;",
                    (store_id, book_id),
                )
                row = self.conn.fetchone()
                if row is None:
                    return error.error_non_exist_book_id(book_id) + (order_id,)

                stock_level = row[1]
                book_info = row[2]
                book_info_json = json.loads(book_info)
                price = book_info_json.get("price")

                if stock_level < count:
                    return error.error_stock_level_low(book_id) + (order_id,)

                self.conn.execute(
                    "UPDATE store set stock_level = stock_level - %s "
                    "WHERE store_id = %s and book_id = %s and stock_level >= %s; ",
                    (count, store_id, book_id, count),
                )
                self.conn.execute(
                    "INSERT INTO new_order_detail(order_id, book_id, count, price) "
                    "VALUES(%s, %s, %s, %s);",
                    (uid, book_id, count, price),
                )


            self.con.commit()
            order_id = uid
        except psycopg2.Error as e:
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
            conn.execute("INSERT INTO history_order SELECT * FROM new_order WHERE order_id=%s",
                                (order_id,))
            conn.execute("UPDATE history_order SET state = 'cancelled' "
                                "WHERE state='wait for payment' AND order_id=%s",
                                (order_id,))            
            conn.execute("INSERT INTO history_order_detail SELECT * FROM new_order_detail "
                                "WHERE order_id=%s",
                                (order_id,))
            conn.execute("DELETE FROM new_order_detail WHERE order_id=%s",
                                (order_id,))
            conn.execute("DELETE FROM new_order WHERE order_id=%s",
                                (order_id,))
        except psycopg2.Error as e:
            logging.error(str(e))
            return 528, "{}".format(str(e))

        except BaseException as e:
            return 530, "{}".format(str(e))
        return error.error_order_timeout(order_id)

    def payment(self, user_id: str, password: str, order_id: str) -> tuple[int, str]:
        conn = self.conn
        try:
            conn.execute(
                "SELECT order_id, user_id, store_id, order_datetime FROM new_order WHERE order_id = %s",
                (order_id,),
            )
            row = conn.fetchone()
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

            conn.execute(
                "SELECT balance, password FROM user_ WHERE user_id = %s;", (buyer_id,)
            )
            row = conn.fetchone()
            if row is None:
                return error.error_non_exist_user_id(buyer_id)
            balance = row[0]
            if password != row[1]:
                return error.error_authorization_fail()

            conn.execute(
                "SELECT store_id, user_id FROM user_store WHERE store_id = %s;",
                (store_id,),
            )
            row = conn.fetchone()
            if row is None:
                return error.error_non_exist_store_id(store_id)

            seller_id = row[1]

            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)

            conn.execute(
                "SELECT book_id, count, price FROM new_order_detail WHERE order_id = %s;",
                (order_id,),
            )
            rows = conn.fetchall()
            total_price = 0
            for row in rows:
                count = row[1]
                price = row[2]
                total_price = total_price + price * count

            if balance < total_price:
                return error.error_not_sufficient_funds(order_id)

            conn.execute(
                "UPDATE user_ set balance = balance - %s "
                "WHERE user_id = %s AND balance >= %s",
                (total_price, buyer_id, total_price),
            )

            conn.execute(
                "UPDATE user_ set balance = balance + %s WHERE user_id = %s",
                (total_price, seller_id),
            )

            # order从new_order中删除并插入history_order中
            conn.execute(
                "INSERT INTO history_order "
                "SELECT * FROM new_order WHERE order_id = %s",
                (order_id,),
            )
            # 更新state为等待发货
            conn.execute(
                "UPDATE history_order "
                "SET state='wait for delivery' "
                "WHERE order_id = %s",
                (order_id,),
            )


            # order_detail从new_order_detail中删除并插入history_order_detail中
            conn.execute(
                "INSERT INTO history_order_detail "
                "SELECT * FROM new_order_detail WHERE order_id=%s",
                (order_id,),
            )
            self.con.commit()
            conn.execute(
                "DELETE FROM new_order_detail where order_id = %s", (order_id,)
            )
            
            conn.execute(
                "DELETE FROM new_order WHERE order_id = %s", (order_id,)
            )
            self.con.commit()

        except psycopg2.Error as e:
            logging.error(str(e))
            return 528, "{}".format(str(e))

        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def add_funds(self, user_id, password, add_value) -> tuple[int, str]:
        try:
            self.conn.execute(
                "SELECT password from user_ where user_id = %s", (user_id,)
            )
            row = self.conn.fetchone()
            if row is None:
                return error.error_authorization_fail()

            if row[0] != password:
                return error.error_authorization_fail()

            self.conn.execute(
                "UPDATE user_ SET balance = balance + %s WHERE user_id = %s",
                (add_value, user_id),
            )
            self.con.commit()
        except psycopg2.Error as e:
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
            if not self.new_order_id_exist(order_id):
                return error.error_invalid_order_id(order_id)
            #修改state状态，并将其从new_order移到history_order
            conn.execute(
                "UPDATE new_order set state='cancelled' "
                "WHERE user_id = %s AND order_id = %s AND state='wait for payment'",
                (user_id,order_id)
            )
            
            conn.execute(
                "INSERT INTO history_order "
                "SELECT * FROM new_order WHERE order_id=%s",
                (order_id,)
            )     
            #将new_order_detail做出相应的改动
            conn.execute(
                "INSERT INTO history_order_detail "
                "SELECT * FROM new_order_detail WHERE order_id=%s",
                (order_id,)
            )
            conn.execute(
                "DELETE FROM new_order_detail "
                "WHERE order_id=%s",
                (order_id,)
            )
            
            conn.execute(
                "DELETE FROM new_order "
                "WHERE order_id=%s",
                (order_id,)
            )
            self.con.commit()
        except psycopg2.Error as e:
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
            
            if not self.his_order_id_exist(order_id):
                return error.error_invalid_order_id(order_id)

            conn.execute(
                "UPDATE history_order SET state='received' "
                "WHERE user_id=%s AND order_id=%s AND state='delivering'",
                (user_id,order_id)
            )

            self.con.commit()
        except psycopg2.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200,"ok"
    
    #如果store_id是空字符串，则为全站搜索，否则是特定store搜索
    def search(self,user_id:str,keyword:str,content:str,store_id:str) -> tuple[(int,str,int)]:
        conn = self.conn
        try:
            self.conn.execute(
                "UPDATE user_ SET bids = %s WHERE user_id = %s",
                ('', user_id),
            )
            self.con.commit()
            
            keys = self.col_book.find_one().keys()
            if keyword not in keys or keyword == '_id':
                return error.error_wrong_keyword(keyword)+(-1,)
            
            sql = """select distinct book_id from store """
            if not store_id == "":
                sql += " where store_id='{}'".format(store_id)
                if not self.store_id_exist(store_id):
                    return error.error_non_exist_store_id(store_id)+(-1,)
            conn.execute(sql)
            row = conn.fetchall()
            if row == []:
                return 200,"ok",0
            bids = list(map(lambda x:x[0],row))
            # bids:tuple[str,]=tuple(map(lambda x:x[0],row))
            # if len(bids) == 1 :
            #     bids="('"+str(bids[0])+"')"
            rows = self.col_book.find({'id': {'$in': bids}, keyword: {'$regex':  content}}, 
                               {'_id': 0, 'id': 1})
            res = list(map(lambda x:x['id'],rows)) 
            # search_sql="""select id from {} 
            #     where id in {} and {} like '%{}%'""".format(book_tb,bids,keyword,content)
            # conn.execute(search_sql)
            # row = conn.fetchall()
            # if row == []:
            #     return 200,"ok",0
            # res = list(map(lambda x:x[0],row))
            bids = ','.join(res)
            conn.execute(
                "UPDATE user_ SET bids = %s WHERE user_id = %s",
                (bids, user_id),
            )
            self.con.commit()
            pages = len(res) // SEARCH_PAGE_LENGTH #结果共几页
        except psycopg2.Error as e:
            logging.error(e)
            return 528, "{}".format(str(e)),-1
        except mongo_error.PyMongoError as e:
            logging.error(e)
            return 529, "{}".format(str(e)),-1
        except BaseException as e:
            logging.error(e)
            return 530, "{}".format(str(e)),-1
        return 200,"ok",pages
    
    def get_book_from_bid(self, user_id: str, have_pic: bool) -> tuple[list[dict]]:
        res = []
        # book_tb = self.book_tb
        # have_pic=False
        if have_pic:
            content = {'_id': 0}
        else:
            content = {'_id': 0, 'picture': 0}
            
        self.conn.execute(
            "select bids from user_ where user_id = %s",
            (user_id,)
        )
        row = self.conn.fetchone()
        bids = row[0].split(',')
        # bids = tuple(row[0].split(','))
        # if len(bids) == 1 :
        #     bids="('"+str(bids[0])+"')"
        # col_user = self.database["user"]
        # row = col_user.find_one({'user_id': user_id}, {'bids': 1})   
        # bids = row["bids"] 
        
        # sql = "select * from {}".format(book_tb)
        # sql += " where id in {}".format(bids)
        # self.conn.execute(sql)
        # res = self.conn.fetchall()
        # self.con.commit()
        col_book = self.col_book
        rows = col_book.find({'id': {'$in': bids}}, content)
        res = [row for row in rows]  
        if have_pic:
            for row in res:
                row['picture']=str(row['picture'])
        return res
    
    def next_page(self, user_id: str, page_now: int, pages: int, have_pic: bool) -> tuple[int, str, list[dict], int]:
        next_page = page_now + 1
        if next_page > pages:
            return error.error_non_exist_page(next_page)+([],page_now,)
        
        bids = self.get_book_from_bid(user_id, have_pic)
        res = bids[next_page * SEARCH_PAGE_LENGTH: (next_page+1) * SEARCH_PAGE_LENGTH:]
        return 200,"ok",res,next_page
    
    def pre_page(self, user_id: str, page_now: int, have_pic: bool) -> tuple[int, str, list[dict], int]:
        pre_page = page_now - 1
        if pre_page < 0:
            return error.error_non_exist_page(pre_page)+([],page_now,)
        
        bids = self.get_book_from_bid(user_id, have_pic)
        res = bids[pre_page * SEARCH_PAGE_LENGTH: (pre_page+1) * SEARCH_PAGE_LENGTH:]
        return 200,"ok",res,pre_page
    
    def specific_page(self, user_id: str, page_now: int, target_page: int, pages: int, have_pic: bool) -> tuple[int, str, list[dict], int]:
        if target_page > pages or target_page < 0:
            return error.error_non_exist_page(target_page)+([],page_now,)
        
        bids = self.get_book_from_bid(user_id, have_pic)
        res = bids[target_page * SEARCH_PAGE_LENGTH: (target_page+1) * SEARCH_PAGE_LENGTH:]
        return 200,"ok",res,target_page

    def history_order(self,user_id:str)->tuple[int,str,list[any]]:
        '''返回order_id,store_id,state,order_datetime,book_id,count,price'''
        conn = self.conn
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)+([],)
            sql="""
                select A.order_id,A.store_id,state,order_datetime,B.book_id,count,price 
                from history_order as A 
                join history_order_detail as B on A.order_id=B.order_id
                join store as C on A.store_id=C.store_id and B.book_id=C.book_id
                where user_id='{}'""".format(user_id)
            conn.execute(sql)
            res = conn.fetchall()
            
            self.con.commit()
        except psycopg2.Error as e:
            return 528, "{}".format(str(e)),[]
        except BaseException as e:
            return 530, "{}".format(str(e)),[]
        return 200,"ok",res