import os
import sqlite3
import logging
import save


def create_dbtable(conn):
    try:       
        conn.execute('DROP TABLE IF EXISTS book')
        conn.execute(
                "CREATE TABLE book ("
                "id TEXT PRIMARY KEY, title TEXT, author TEXT, "
                "publisher TEXT, original_title TEXT, "
                "translator TEXT, pub_year TEXT, pages INTEGER, "
                "price INTEGER, currency_unit TEXT, binding TEXT, "
                "isbn TEXT, author_intro TEXT, book_intro text, "
                "content TEXT, tags TEXT, picture BLOB)"
            )
        conn.commit()
    except sqlite3.Error as e:
        logging.error(str(e))
        conn.rollback()

  
    
def insert_books(cursor, conn):
    sql = (
            "INSERT INTO book("
            "id, title, author, "
            "publisher, original_title, translator, "
            "pub_year, pages, price, "
            "currency_unit, binding, isbn, "
            "author_intro, book_intro, content, "
            "tags, picture)"
            "VALUES("
            "?, ?, ?, "
            "?, ?, ?, "
            "?, ?, ?, "
            "?, ?, ?, "
            "?, ?, ?, "
            "?, ?)"
        )
    for row in cursor:
        conn.execute(sql, row)
        conn.commit()
    conn.close()



cursor = save.get_book_cursor(0, 15, True)
database = "book.db"
conn = sqlite3.connect(database)
#print(books)    
create_dbtable(conn)
insert_books(cursor, conn)
