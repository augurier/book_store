import requests
import simplejson
from urllib.parse import urljoin
from fe.access.auth import Auth
from fe.conf import Has_picture

class Buyer:
    def __init__(self, url_prefix, user_id, password):
        self.url_prefix = urljoin(url_prefix, "buyer/")
        self.user_id = user_id
        self.password = password
        self.token = ""
        self.terminal = "my terminal"
        self.auth = Auth(url_prefix)
        code, self.token = self.auth.login(self.user_id, self.password, self.terminal)
        assert code == 200

    def new_order(self, store_id: str, book_id_and_count: tuple[(str, int)]) -> tuple[int, str]:
        books = []
        for id_count_pair in book_id_and_count:
            books.append({"id": id_count_pair[0], "count": id_count_pair[1]})
        json = {"user_id": self.user_id, "store_id": store_id, "books": books}
        # print(simplejson.dumps(json))
        url = urljoin(self.url_prefix, "new_order")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        response_json = r.json()
        return r.status_code, response_json.get("order_id")

    def payment(self, order_id: str):
        json = {
            "user_id": self.user_id,
            "password": self.password,
            "order_id": order_id,
        }
        url = urljoin(self.url_prefix, "payment")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code

    def add_funds(self, add_value: str) -> int:
        json = {
            "user_id": self.user_id,
            "password": self.password,
            "add_value": add_value,
        }
        url = urljoin(self.url_prefix, "add_funds")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code

    def cancel_order(self, order_id: str) -> int:
        json = {
            "user_id": self.user_id,
            "order_id": order_id,
        }
        url = urljoin(self.url_prefix, "cancel_order")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code

    def receive(self, order_id: str) -> int:
        json = {
            "user_id": self.user_id,
            "order_id": order_id,
        }
        url = urljoin(self.url_prefix, "receive")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code

    def search(self,keyword,content,store_id="",have_pic=Has_picture)->tuple[int,int]:
        json={
            "user_id":self.user_id,
            "keyword":keyword,
            "content":content,
            "store_id":store_id,
            "have_pic":have_pic
        }
        url=urljoin(self.url_prefix,"search")
        headers={"token":self.token}
        r=requests.post(url,headers=headers,json=json)
        response_json=r.json()
        # bids_json=response_json.get("bids")
        pages_json=response_json.get("pages")
        return r.status_code,pages_json

    def next_page(self, page_now: int, pages: int,have_pic=Has_picture) -> tuple[int, str, list[str], int]:
        json={
            "user_id":self.user_id,
            "page_now":page_now,
            "pages":pages,
            "have_pic":have_pic
        }
        url=urljoin(self.url_prefix,"next_page")
        headers={"token":self.token}
        r=requests.post(url,headers=headers,json=json)
        response_json=r.json()
        bids_json=response_json.get("bids")
        page_json=response_json.get("page")
        return r.status_code,bids_json,page_json

    def pre_page(self,  page_now: int,have_pic=Has_picture) -> tuple[int, str, list[str], int]:
        json={
            "user_id":self.user_id,
            "page_now":page_now,
            "have_pic":have_pic
        }
        url=urljoin(self.url_prefix,"pre_page")
        headers={"token":self.token}
        r=requests.post(url,headers=headers,json=json)
        response_json=r.json()
        bids_json=response_json.get("bids")
        page_json=response_json.get("page")
        return r.status_code,bids_json,page_json
    
    def specific_page(self, page_now: int, target_page: int, pages: int,have_pic=Has_picture) -> tuple[int, str, list[str], int]:
        json={
            "user_id":self.user_id,
            "page_now":page_now,
            "target_page":target_page,
            "pages":pages,
            "have_pic":have_pic
        }
        url=urljoin(self.url_prefix,"specific_page")
        headers={"token":self.token}
        r=requests.post(url,headers=headers,json=json)
        response_json=r.json()
        bids_json=response_json.get("bids")
        page_json=response_json.get("page")
        return r.status_code,bids_json,page_json
    
    
    def history_order(self)->tuple[int,list[any]]:
        json={
            "user_id":self.user_id,
        }
        url=urljoin(self.url_prefix,"history_order")
        headers={"token":self.token}
        r=requests.post(url,headers=headers,json=json)
        response_json=r.json()
        history_order_json=response_json.get("history_order")
        return r.status_code,history_order_json