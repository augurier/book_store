import os
import sqlite3
import pymongo

def get_book_cursor():
        parent_path = os.path.dirname(os.path.dirname(__file__))
        book_db = os.path.join(parent_path, "data/book_lx.db")          
        conn = sqlite3.connect(book_db)
        cursor = conn.execute(
            "SELECT id, title, author, "
            "publisher, original_title, "
            "translator, pub_year, pages, "
            "price, currency_unit, binding, "
            "isbn, author_intro, book_intro, "
            "content, tags, picture FROM book ORDER BY id "
        )
        return cursor




myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["bookstore_db"]
mydb['book_lx'].drop()
mycol = mydb["book_lx"]
mycol.create_index([("id", 1)], unique=True)
cursor = get_book_cursor()
booklist = []
cnt = 0
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
    #print(book['title'])
    cnt += 1
    booklist.append(book)
    
result = mycol.insert_many(booklist)
print("successfully save {} books!".format(cnt))