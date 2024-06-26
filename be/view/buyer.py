from flask import Blueprint
from flask import request
from flask import jsonify
from be.model.buyer import Buyer

bp_buyer = Blueprint("buyer", __name__, url_prefix="/buyer")


@bp_buyer.route("/new_order", methods=["POST"])
def new_order():
    user_id: str = request.json.get("user_id")
    store_id: str = request.json.get("store_id")
    books: [] = request.json.get("books")
    id_and_count = []
    for book in books:
        book_id = book.get("id")
        count = book.get("count")
        id_and_count.append((book_id, count))

    b = Buyer()
    code, message, order_id = b.new_order(user_id, store_id, id_and_count)
    return jsonify({"message": message, "order_id": order_id}), code


@bp_buyer.route("/payment", methods=["POST"])
def payment():
    user_id: str = request.json.get("user_id")
    order_id: str = request.json.get("order_id")
    password: str = request.json.get("password")
    b = Buyer()
    code, message = b.payment(user_id, password, order_id)
    return jsonify({"message": message}), code


@bp_buyer.route("/add_funds", methods=["POST"])
def add_funds():
    user_id = request.json.get("user_id")
    password = request.json.get("password")
    add_value = request.json.get("add_value")
    b = Buyer()
    code, message = b.add_funds(user_id, password, add_value)
    return jsonify({"message": message}), code


@bp_buyer.route("/cancel_order", methods=["POST"])
def cancel_order():
    user_id = request.json.get("user_id")
    order_id = request.json.get("order_id")
    b = Buyer()
    code, message = b.cancel_order(user_id, order_id)
    return jsonify({"message": message}), code


@bp_buyer.route("/receive", methods=["POST"])
def receive():
    user_id = request.json.get("user_id")
    order_id = request.json.get("order_id")
    b = Buyer()
    code, message = b.receive(user_id, order_id)
    return jsonify({"message": message}), code

@bp_buyer.route("/search", methods=["POST"])
def search():
    user_id=request.json.get("user_id")
    keyword=request.json.get("keyword")
    content=request.json.get("content")
    store_id=request.json.get("store_id")
    b=Buyer()
    code,message,pages=b.search(user_id,keyword,content,store_id)
    return jsonify({'message':message,'pages':pages}),code

@bp_buyer.route("/next_page", methods=["POST"])
def next_page():
    user_id=request.json.get("user_id")
    page_now=request.json.get("page_now")
    pages=request.json.get("pages")
    have_pic=request.json.get("have_pic")

    b=Buyer()
    code,message,bids,page=b.next_page(user_id,page_now,pages,have_pic)
    return jsonify({'message':message,'bids':bids,'page':page}),code

@bp_buyer.route("/pre_page", methods=["POST"])
def pre_page():
    user_id=request.json.get("user_id")
    page_now=request.json.get("page_now")
    have_pic=request.json.get("have_pic")

    b=Buyer()
    code,message,bids,page=b.pre_page(user_id,page_now,have_pic)
    return jsonify({'message':message,'bids':bids,'page':page}),code

@bp_buyer.route("/specific_page", methods=["POST"])
def specific_page():
    user_id=request.json.get("user_id")
    target_page=request.json.get("target_page")
    page_now=request.json.get("page_now")
    pages=request.json.get("pages")
    have_pic=request.json.get("have_pic")

    b=Buyer()
    code,message,bids,page=b.specific_page(user_id,page_now,target_page,pages,have_pic)
    return jsonify({'message':message,'bids':bids,'page':page}),code

@bp_buyer.route("/history_order",methods=["POST"])
def history_order():
    user_id=request.json.get("user_id")
    b=Buyer()
    code,message,history_order=b.history_order(user_id)
    return jsonify({'message':message,"history_order":history_order}),code