#将书本存入本地mongodb
import os
import sqlite3
import pymongo

def get_book_cursor(start, size, islarge=False):
        books = []
        parent_path = os.path.dirname(os.path.dirname(__file__))
        if islarge:
            book_db = os.path.join(parent_path, "data/book_lx.db")
        else:
            book_db = os.path.join(parent_path, "data/book.db")            
        conn = sqlite3.connect(book_db)
        cursor = conn.execute(
            "SELECT id, title, author, "
            "publisher, original_title, "
            "translator, pub_year, pages, "
            "price, currency_unit, binding, "
            "isbn, author_intro, book_intro, "
            "content, tags, picture FROM book ORDER BY id "
            "LIMIT ? OFFSET ?",
            (size, start),
        )
        return cursor

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["bookstore_db"]
mycol = mydb["book"]
mycol.delete_many({})
mycol.create_index([("id", 1)], unique=True)
cursor = get_book_cursor(0, 15)
booklist = []
for row in cursor:
    book = {
            'id' : row[0],
            'title' : row[1],
            'author' : row[2],
            'publisher' : row[3],
            'original_title' : row[4],
            'translator' : row[5],
            'pub_year' : row[6],
            'pages' : row[7],
            'price' : row[8],
            'currency_unit' : row[9],
            'binding' : row[10],
            'isbn' : row[11],
            'author_intro' : row[12],
            'book_intro' : row[13],
            'content' : row[14],
            'tags' : row[15],
            'picture' : row[16],
    }
    print(book['title'])
    booklist.append(book)
    
result = mycol.insert_many(booklist)

# content = mycol.find()
# for each in content:
#     print(each['title'])