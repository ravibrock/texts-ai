from datasets import Dataset
import os.path
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
def query(conn, sql):
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()

    return rows


# Turns a list into a dataset dict
def list2dataset(dataset):
    return Dataset.from_list([{"text": x} for x in dataset])


# Processes the data into the right format
def slice_by_sender(data):
    # Slices data into threads
    new_data = []
    temp_new_data = []
    for row in range(len(data) - 1):
        if data[row][0] == data[row + 1][0]:
            temp_new_data.append(data[row])
        else:
            new_data.append(temp_new_data)
            temp_new_data = []

    # Filters messages so I'm always replying and trims each thread to 10 messages/reply pairs
    data = []
    for row in range(len(new_data)):
        if new_data[row]:
            if new_data[row][0][1] == 1:
                new_data[row].pop(0)
        if len(new_data[row]) >= 20:
            data.append(new_data[row][:(len(new_data[row]) - (len(new_data[row]) % 20))])

    # Extracts text from tuples
    for row in range(len(data)):
        for row2 in range(len(data[row])):
            data[row][row2] = data[row][row2][3]

    # Slices each thread into 20-message chunks
    new_data = []
    for row in range(len(data)):
        new_data_slice = [data[row][x:x + 20] for x in range(0, len(data[row]), 20)]
        for row2 in new_data_slice:
            new_data.append(row2)

    # Joins each list of message/reply pairs into a string with <|endoftext|> special tokens
    data = list(map("<|endoftext|>".join, new_data))

    return data


# Gets the messages from the database
def get_messages():
    db_file = os.path.expanduser("~/Library/Messages/chat.db")
    conn = create_connection(db_file)
    conn.create_function("REGEXP", 2, regexp)
    with open("query.sql", "r") as sql_file:
        sql = sql_file.read().replace("\\n", "\n")
    rows = query(conn, sql)

    return list2dataset(slice_by_sender(rows))
