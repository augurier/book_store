#���Բ鿴.db�ļ�����
import os
import sqlite3


parent_path = os.path.dirname(os.path.dirname(__file__))
book_db = os.path.join(parent_path, "data/book.db")#�޸���鿴���ļ�
conn = sqlite3.connect(book_db)
cursor = conn.execute("select * from book")#�޸���鿴������
for row in cursor:
    print(row)