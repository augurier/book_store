import os
import sqlite3
import psycopg2
def get_book_cursor(islarge=False):
        parent_path = os.path.dirname(os.path.dirname(__file__))
        if islarge:
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
            (15, 0)
            )
        return cursor

def connect_pg():
    conn = psycopg2.connect(
    host="localhost",
    database="bookstore_db",
    user="postgres",
    password="lidu12345"
)
    return conn

def init_book_table(cur):
    sql = "DROP TABLE IF EXISTS book"
    cur.execute(sql)
    sql = "DROP TABLE IF EXISTS book_lx"
    cur.execute(sql)
    
    sql = '''CREATE TABLE book(
            id TEXT primary key,
            title TEXT,
            author TEXT,
            publisher TEXT,
            original_title TEXT,
            translator TEXT,
            pub_year TEXT,
            pages INTEGER,
            price INTEGER,
            currency_unit TEXT,
            binding TEXT,
            isbn TEXT)
        '''
    cur.execute(sql)
    
    sql = '''CREATE TABLE book_lx(
        id TEXT primary key,
        title TEXT,
        author TEXT,
        publisher TEXT,
        original_title TEXT,
        translator TEXT,
        pub_year TEXT,
        pages INTEGER,
        price INTEGER,
        currency_unit TEXT,
        binding TEXT,
        isbn TEXT)
    '''
    cur.execute(sql)

def save_book(cur, islarge=False):
    if islarge:
        cursor = get_book_cursor(True)
        db = "book_lx"
    else:
        cursor = get_book_cursor()
        db = "book"
    booklist = []
    for row in cursor:
        # print(row[0:12:])
        booklist.append(row[0:12:])
    sql = '''
            insert into {} (id, title, author, 
                publisher, original_title, 
                translator, pub_year, pages, 
                price, currency_unit, binding, isbn)
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''.format(db)
    cur.executemany(sql, booklist)

def check(cur):
    cur.execute("SELECT * FROM book")
    rows = cur.fetchall()
    print("table book has {} books!".format(len(rows)))
    
    cur.execute("SELECT * FROM book_lx")
    rows = cur.fetchall()
    print("table book_lx has {} books!".format(len(rows)))

def close(conn, cur):
    conn.commit()
    cur.close()
    conn.close()

conn = connect_pg()
cur = conn.cursor()
init_book_table(cur)
save_book(cur)
save_book(cur, True)
check(cur)
close(conn, cur)
