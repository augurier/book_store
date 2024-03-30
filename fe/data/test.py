#粗略查看.db文件内容
import os
import sqlite3


parent_path = os.path.dirname(os.path.dirname(__file__))
book_db = os.path.join(parent_path, "data/book.db")#修改需查看的文件
conn = sqlite3.connect(book_db)
cursor = conn.execute("select * from book")#修改需查看的内容
for row in cursor:
    print(row)