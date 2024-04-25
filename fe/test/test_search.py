import pytest

from fe.access.buyer import Buyer
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
from fe.access.new_seller import register_new_seller
from fe.access.book import Book
import uuid
import time
import logging
class TestSearch:
    seller_id: str
    store_id: str
    buyer_id: str
    password: str
    buy_book_info_list: list[Book]
    total_price: int
    order_id: str
    buyer: Buyer

    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_id = "test_search_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_search_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_search_buyer_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id
        gen_book = GenBook(self.seller_id, self.store_id)
        ok, buy_book_id_list = gen_book.gen(
            non_exist_book_id=False, low_stock_level=False
        )
        self.buy_book_info_list = gen_book.buy_book_info_list
        assert ok
        b = register_new_buyer(self.buyer_id, self.password)
        self.buyer = b
        code, self.order_id = b.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        self.total_price = 0
        for item in self.buy_book_info_list:
            book: Book = item[0]
            num = item[1]
            if book.price is None:
                continue
            else:
                self.total_price = self.total_price + book.price * num
        yield

    def test_ok(self):
        book:Book=self.buy_book_info_list[0][0]
        code,pages=self.buyer.search('title',book.title)
        assert code == 200 and pages == 0
        # assert book.id in bids and pages == 0
    
    def test_not_in(self):
        book:Book=self.buy_book_info_list[0][0]
        code,pages=self.buyer.search('title',book.title+"_x")
        assert code == 200 and pages == 0
        # assert len(bids) == 0 and pages == 0
        
    def test_next_and_pre(self):
        code,pages=self.buyer.search('tags', '\n')
        assert code == 200 and pages > 0
        code,bids,page=self.buyer.specific_page(0,0,pages)
        book=bids[0]
        code,bids1,page=self.buyer.next_page( 0, pages)
        assert code == 200 and page == 1
        code,bids0,page=self.buyer.pre_page( 1)
        assert code == 200 and page == 0 and book in bids0
        
    def test_specific_page(self):
        code,pages=self.buyer.search('tags', '\n')
        assert code == 200 and pages > 0
        code,bids,page=self.buyer.specific_page(0,0,pages)
        book=bids[0]
        code,bids0,page=self.buyer.specific_page(0, 0,pages)
        assert code == 200 and page == 0 and book in bids0
        
    def test_non_next_and_pre_and_specific(self):
        book:Book=self.buy_book_info_list[0][0]
        code,pages=self.buyer.search('title',book.title)
        assert code == 200 and pages == 0
        code,bids0,page=self.buyer.next_page(0, pages)
        assert code != 200
        code,bids0,page=self.buyer.pre_page(0)
        assert code != 200
        code,bids0,page=self.buyer.specific_page(0, 1,pages)
        assert code != 200
        
    def test_partial_name(self):
        book:Book=self.buy_book_info_list[0][0]
        code,pages=self.buyer.search('title',book.title[0])
        assert code == 200
        code,bids,pages=self.buyer.specific_page(0,0,pages)
        assert book.id in [row['id'] for row in bids]

    def test_wrong_keyword(self):
        book:Book=self.buy_book_info_list[0][0]
        code,pages=self.buyer.search('wrong',book.title[0])
        assert code != 200

    def test_specific_store(self):
        seller_id = "test_search_seller_id_{}".format(str(uuid.uuid1()))
        store_id = "test_search_store_id_{}".format(str(uuid.uuid1()))
        book:Book=self.buy_book_info_list[0][0]
        gen_book=GenBook(seller_id,store_id)
        gen_book.gen(False,False,1)
        code,pages = self.buyer.search('title',book.title,store_id=self.store_id)
        assert code == 200 and pages == 0
        code,bids,pages=self.buyer.specific_page(0,0,pages)
        assert book.id in [row['id'] for row in bids]
        code,pages = self.buyer.search('title',book.title,store_id=store_id)
        code,bids,pages=self.buyer.specific_page(0,0,pages)
        assert code == 200 and not book.id in [row['id'] for row in bids] and pages == 0

    def test_wrong_store_id(self):
        book:Book=self.buy_book_info_list[0][0]
        code,pages=self.buyer.search('title',book.title,store_id=self.store_id+'_x')
        assert code != 200

    def test_zero_stock(self):
        seller_id = "test_search_seller_id_{}".format(str(uuid.uuid1()))
        store_id = "test_search_store_id_{}".format(str(uuid.uuid1()))
        password=seller_id
        seller=register_new_seller(seller_id,password)
        seller.create_store(store_id)
        code,pages=self.buyer.search('title','abc',store_id=store_id)
        assert code == 200 and pages == 0
        code,bids,pages=self.buyer.specific_page(0,0,pages)
        assert bids==[]