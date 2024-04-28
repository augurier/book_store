import time
import pymongo.errors as mongo_error
import uuid
import json
import logging
from be.model import db_conn
from be.model import error
from be.model import order_handle

SEARCH_PAGE_LENGTH = 10

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

            col_store = self.database['store']
            col_new_order_detail = self.database['new_order_detail']
            col_new_order = self.database['new_order']

            
            for book_id, count in id_and_count:
                row = col_store.find_one({'store_id': store_id, 'books.book_id': book_id},
                                     {'_id': 0, 'books.$': 1})
                if row is None:
                    return error.error_non_exist_book_id(book_id) + (order_id,)

                stock_level = row['books'][0]['stock_level']
                book_id = row['books'][0]['book_id']
                row = self.col_book.find_one({'id': book_id},{'_id': 0, 'price': 1})
                price = row['price']

                if stock_level < count:
                    return error.error_stock_level_low(book_id) + (order_id,)
                
                rows = col_store.update_one({'store_id': store_id, 'books.book_id': book_id, 'books.stock_level': {'$gte': count}}, 
                                           {'$inc': {'books.$.stock_level': -count}})
                if rows.matched_count != 1:
                    return error.error_stock_level_low(book_id) + (order_id,)

                detail1 = {
                        'order_id' : uid,
                        'book_id' : book_id,
                        'count' : count,
                        'price' : price
                    }
                col_new_order_detail.insert_one(detail1)
            
            cur_time = str(int(time.time())) #纪元以来的秒数
            order1 = {
                        'order_id' : uid,
                        'store_id' : store_id,
                        'user_id' : user_id,
                        'state' : 'wait for payment',
                        'order_datetime' : cur_time
                    }
            col_new_order.insert_one(order1)

            order_id = uid          
        except mongo_error.PyMongoError as e:
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            return 530, "{}".format(str(e)), ""  

        return 200, "ok", order_id
    
    #?????????????????order_id???
    def order_timeout(self,order_id:str) -> tuple[(int,str)]:
        col_his_order = self.database["his_order"]
        col_new_order = self.database["new_order"]
        col_his_order_detail = self.database["his_order_detail"]
        col_new_order_detail = self.database["new_order_detail"]
        try:
            order_handle.new_to_his(col_new_order, col_his_order, order_id)
            order_handle.set_order_state(col_his_order, order_id, 'cancelled', 'wait for payment')
            order_handle.new_to_his(col_new_order_detail, col_his_order_detail, order_id)

        except mongo_error.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        
        return error.error_order_timeout(order_id)



    def payment(self, user_id: str, password: str, order_id: str) -> tuple[(int, str)]:
        try:
            col_user = self.database["user"]
            col_store = self.database["store"]
            col_new_order = self.database["new_order"]
            col_new_order_detail = self.database["new_order_detail"]            
            col_his_order = self.database["his_order"]
            col_his_order_detail = self.database["his_order_detail"]
            
            row = col_new_order.find_one({'order_id': order_id}, {'_id': 0, 'state': 0})

            if row is None:
                return error.error_invalid_order_id(order_id)

            order_id = row['order_id']
            buyer_id = row['user_id']
            store_id = row['store_id']
            order_datetime = int(row['order_datetime'])
            
            if buyer_id != user_id:
                return error.error_authorization_fail()

            timeout_limit = 1 #???????????????1?????????
            if order_datetime + timeout_limit < int(time.time()):
                return self.order_timeout(order_id)

            row = col_user.find_one({'user_id': buyer_id}, {'_id': 0, 'balance': 1, 'password': 1})
            if row is None:
                return error.error_non_exist_user_id(buyer_id)
            balance = row['balance']
            if password != row['password']:
                return error.error_authorization_fail()

            row = col_store.find_one({'store_id': store_id}, 
                                          {'_id': 0, 'store_id': 1, 'user_id': 1})
            if row is None:
                return error.error_non_exist_store_id(store_id)
            seller_id = row['user_id']
            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)

            rows = col_new_order_detail.find({'order_id': order_id}, 
                                             {'_id': 0, 'book_id': 1, 'count': 1, 'price': 1})
            total_price = 0
            for row in rows:
                count = row['count']
                price = row['price']
                total_price = total_price + price * count
            if balance < total_price:
                return error.error_not_sufficient_funds(order_id)

            rows = col_user.update_one({'user_id': buyer_id, 'balance': {'$gte': total_price}}, 
                                           {'$inc': {'balance': -total_price}})
            if rows.matched_count != 1:
                return error.error_not_sufficient_funds(order_id)
            
            rows = col_user.update_one({'user_id': seller_id}, {'$inc': {'balance': total_price}})
            if rows.matched_count != 1:
                return error.error_non_exist_user_id(seller_id)

            # order??new_order???????????history_order??
            # ????state????????
            if not order_handle.new_to_his(col_new_order, col_his_order, order_id):
                return error.error_invalid_order_id(order_id)            
            if not order_handle.set_order_state(col_his_order, order_id, 'wait for delivery'):
                return error.error_invalid_order_id(order_id)

            # order_detail??new_order_detail???????????history_order_detail??
            if not order_handle.new_to_his(col_new_order_detail, col_his_order_detail, order_id):
                return error.error_invalid_order_id(order_id)

        except mongo_error.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))


        return 200, "ok"

    def add_funds(self, user_id, password, add_value) -> tuple[(int, str)]:
        try:
            col_user = self.database["user"]
            row = col_user.find_one({'user_id': user_id}, {'_id': 0, 'password': 1})
            if row is None:
                return error.error_authorization_fail()
            if row['password'] != password:
                return error.error_authorization_fail()

            rows = col_user.update_one({'user_id': user_id}, {'$inc': {'balance': add_value}})
            if rows.matched_count != 1:
                return error.error_non_exist_user_id(user_id)
            
        except mongo_error.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def cancel_order(self, user_id: str, order_id: str) -> tuple[int, str]:
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
                       
            col_new_order = self.database["new_order"]
            col_new_order_detail = self.database["new_order_detail"]            
            col_his_order = self.database["his_order"]
            col_his_order_detail = self.database["his_order_detail"]

            #???state???????????new_order???history_order
            if not order_handle.set_order_state(col_new_order, order_id, 'cancelled', 'wait for payment'):
                return error.error_invalid_order_id(order_id)
            if not order_handle.new_to_his(col_new_order, col_his_order, order_id):
                return error.error_invalid_order_id(order_id)
            
            #??new_order_detail???????????
            if not order_handle.new_to_his(col_new_order_detail, col_his_order_detail, order_id):
                return error.error_invalid_order_id(order_id)

        except mongo_error.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
                
        return 200, "ok"

    def receive(self, user_id: str, order_id: str) -> tuple[(int,str)]:
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)

            col_his_order = self.database["his_order"]
            if not order_handle.set_order_state(col_his_order, order_id, 'received', 'delivering'):
                return error.error_invalid_order_id(order_id)

        except mongo_error.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"
    
    #如果store_id是空字符串，则为全站搜索，否则是特定store搜索
    def search(self, user_id:str, keyword:str, content:str, store_id:str) -> tuple[int, str, int]:
        try:    
            col_store = self.database["store"]
            keys = self.col_book.find_one().keys()
            if keyword not in keys or keyword == '_id':
                return error.error_wrong_keyword(keyword)+(-1,)
                
            if store_id == '':
                target_store = {}
            else:
                if not self.store_id_exist(store_id):
                    return error.error_non_exist_store_id(store_id)+(-1,)  
                              
                target_store = {'store_id': store_id}
                
            rows = col_store.find(target_store, {'_id': 0, 'books.book_id': 1})
            books = [row['books'] for row in rows]
            bids = []
            for book in books:
                bids += [row['book_id'] for row in book]

            rows = self.col_book.find({'id': {'$in': bids}, keyword: {'$regex':  content}}, 
                               {'_id': 0, 'id': 1})
            res = [row['id'] for row in rows]
            
            col_user = self.database["user"]
            rows = col_user.update_one({'user_id': user_id}, {'$set': {'bids': res}})
            
            pages = len(res) // SEARCH_PAGE_LENGTH #结果共几页
            
        except mongo_error.PyMongoError as e:
            return 528, "{}".format(str(e)),-1
        except BaseException as e:
            logging.error(e)
            return 530, "{}".format(str(e)),-1
        
        return 200,"ok",pages
    
    def get_book_from_bid(self, user_id: str, have_pic: bool) -> tuple[list[dict]]:
        res = []
        # have_pic=False
        if have_pic:
            content = {'_id': 0}
        else:
            content = {'_id': 0, 'picture': 0}
        
        col_user = self.database["user"]
        row = col_user.find_one({'user_id': user_id}, {'bids': 1})   
        bids = row["bids"] 
        
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

    def history_order(self, user_id:str) -> tuple[int, str, list[any]]:
        '''return order_id,store_id,state,order_datetime,book_id,count,price''' 
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)+([],)
                    
            col_his_order = self.database["his_order"]
            
            match1 = {'$match': {'user_id': user_id}}
            look_up1 = {'$lookup': {'from': 'his_order_detail', 
                                   'localField': 'order_id', 
                                   'foreignField': 'order_id', 
                                   'as': 'order_detail'}} 
            look_up2 = {'$lookup':{'from': 'store',
                                   'localField': 'store_id',
                                   'foreignField': 'store_id',
                                   'as': 'store_item'}}
            project = {'$project': {'_id': 0, 'order_id': 1, 'store_id': 1, 'state': 1, 'order_datetime': 1,
                                    'book_id': '$order_detail.book_id', 'count': '$order_detail.count', 'price': '$order_detail.price',
                                    'difference': {'$in': ['$order_detail.book_id', '$store_item.books.book_id']}}}
            match2 = {'$match': {'difference': True}}
            rows = col_his_order.aggregate([match1, look_up1, look_up2, project, match2])   
            res = [[row['order_id'], row['store_id'], row['state'], row['order_datetime'], row['book_id'], row['count'], row['price']] for row in rows]        
            # sql="""
            #     select A.order_id,A.store_id,state,order_datetime,B.book_id,count,price 
            #     from history_order as A 
            #     join history_order_detail as B on A.order_id=B.order_id
            #     join store as C on A.store_id=C.store_id and B.book_id=C.book_id
            #     where user_id='{}'""".format(user_id)
            
        except mongo_error.PyMongoError as e:
            logging.error(str(e))
            return 528, "{}".format(str(e)),[]
        except BaseException as e:
            logging.error(str(e))
            return 530, "{}".format(str(e)),[]
        
        return 200,"ok",res