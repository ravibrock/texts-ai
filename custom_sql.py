import re
import sqlite3


# Regex function for SQLite
def regexp(expr, item):
    reg = re.compile(expr)
    return reg.search(item) is not None


# Creates a connection to the database file
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(e)

    return conn


# Queries the messages database
def query(db_file, sql):
    conn = create_connection(db_file)
    conn.create_function("REGEXP", 2, regexp)
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()

    return rows
