import os
import sqlite3


parent_path = os.path.dirname(os.path.dirname(__file__))
book_db = os.path.join(parent_path, "data/book.db")
conn = sqlite3.connect(book_db)
cursor = conn.execute("select * from book")
for row in cursor:
    print(row)