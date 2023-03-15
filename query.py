from datasets import Dataset
import os.path
import sqlite3


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(e)

    return conn


def query(conn, sql):
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()

    return rows


def list2dataset(dataset):
    return Dataset.from_list([{"text": x} for x in dataset])


def get_messages(return_messages, return_replies):
    db_file = os.path.expanduser("~/Library/Messages/chat.db")
    conn = create_connection(db_file)
    sql = "SELECT b.text AS msg, a.text AS reply " \
          "FROM main.message AS a, main.message AS b " \
          "WHERE a.reply_to_guid = b.guid " \
          "AND a.is_from_me IS 1 " \
          "AND b.is_from_me IS NOT 1 " \
          "AND a.text <> '' " \
          "AND b.text <> '' " \
          "AND a.is_delivered IS 1 " \
          "AND b.is_delivered IS 1 " \
          "AND a.balloon_bundle_id IS NULL " \
          "AND b.balloon_bundle_id IS NULL " \
          "AND a.cache_has_attachments IS 0 " \
          "AND b.cache_has_attachments IS 0;"
    rows = query(conn, sql)

    messages = []
    replies = []
    for row in rows:
        messages.append(row[0])
        replies.append(row[1])

    messages = list2dataset(messages)
    replies = list2dataset(replies)

    if return_messages and not return_replies:
        return messages
    if not return_messages and return_replies:
        return replies
    if return_messages and return_replies:
        return messages, replies
