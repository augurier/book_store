#粗略查看.db文件内容
import os
import sqlite3


parent_path = os.path.dirname(os.path.dirname(__file__))
book_db = os.path.join(parent_path, "../book.db")#修改需查看的文件
print(book_db)
conn = sqlite3.connect(book_db)
cursor = conn.execute("select * from book")#修改需查看的内容
# print(len(cursor))
for row in cursor:
    print(row[0:3])
    # print(len(row))