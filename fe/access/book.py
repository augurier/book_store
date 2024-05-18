import os
import sqlite3 as sqlite
import random
import base64
import simplejson as json
from be.model import store

class Book:
    id: str
    title: str
    author: str
    publisher: str
    original_title: str
    translator: str
    pub_year: str
    pages: int
    price: int
    currency_unit: str
    binding: str
    isbn: str
    author_intro: str
    book_intro: str
    content: str
    tags: [str]
    pictures: [bytes]

    def __init__(self):
        self.tags = []
        self.pictures = []


class BookDB:
    def __init__(self, large: bool = False):
        self.con = store.get_db_conn()
        self.conn = self.con.cursor()
        if large:
            self.book_tb = 'book_lx'
        else:
            self.book_tb = 'book'

    def get_book_count(self):
        self.conn.execute("SELECT count(id) FROM {}".format(self.book_tb))
        row = self.conn.fetchone()
        return row[0]

    def get_book_info(self, start, size) -> [Book]:
        books = []
        self.conn.execute(
            "SELECT id, title, author, "
            "publisher, original_title, "
            "translator, pub_year, pages, "
            "price, currency_unit, binding, "
            "isbn FROM book ORDER BY id "
            "LIMIT %s OFFSET %s",
            (size, start),
        )
        cursor = self.conn.fetchall()
        for row in cursor:
            book = Book()
            book.id = row[0]
            book.title = row[1]
            book.author = row[2]
            book.publisher = row[3]
            book.original_title = row[4]
            book.translator = row[5]
            book.pub_year = row[6]
            book.pages = row[7]
            book.price = row[8]

            book.currency_unit = row[9]
            book.binding = row[10]
            book.isbn = row[11]

            # for tag in tags.split("\n"):
            #     if tag.strip() != "":
            #         book.tags.append(tag)
            # for i in range(0, random.randint(0, 9)):
            #     if picture is not None:
            #         encode_str = base64.b64encode(picture).decode("utf-8")
            #         book.pictures.append(encode_str)
            books.append(book)
            # print(tags.decode('utf-8'))

            # print(book.tags, len(book.picture))
            # print(book)
            # print(tags)

        return books
