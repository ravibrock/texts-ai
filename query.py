import argparse
import custom_sql
import os.path


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

    # Filters messages so I'm always replying and joins into a single string
    data = []
    # seq_len = 20
    for row in range(len(new_data)):
        if len(new_data[row]) > 0:
            if new_data[row][0][1] == 1:
                new_data[row].pop(0)
            new_data[row] = [f"\n\nMESSAGE:\n{x[3]}" if x[1] == 0 else f"\n\nREPLY:\n{x[3]}" for x in new_data[row]]
            data.append(new_data[row])

    return "".join(list(map(" ".join, data)))[2:]


# Gets the messages from the database
def main():
    db_file = os.path.expanduser("~/Library/Messages/chat.db")
    with open("sql/all_messages.sql", "r") as sql_file:
        sql = sql_file.read().replace("\\n", "\n")
    messages = slice_by_sender(custom_sql.query(db_file, sql))

    parser = argparse.ArgumentParser("Query messages")
    parser.add_argument("write_path", help="Path to write processed messages database to.", type=str)
    file = os.path.expanduser(parser.parse_args().write_path)

    with open(file, "w") as f:
        f.write(messages)


if __name__ == "__main__":
    main()
