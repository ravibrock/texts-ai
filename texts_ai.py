import argparse
import generate.gpt
import generate.llama
import multiprocessing
import os
import custom_sql
import time
import datetime


class suppress_stdout_stderr(object):
    def __init__(self):
        # Open a pair of null files
        self.null_fds = [os.open(os.devnull, os.O_RDWR) for x in range(2)]
        # Save the actual stdout (1) and stderr (2) file descriptors.
        self.save_fds = [os.dup(1), os.dup(2)]

    def __enter__(self):
        # Assign the null pointers to stdout and stderr.
        os.dup2(self.null_fds[0], 1)
        os.dup2(self.null_fds[1], 2)

    def __exit__(self, *_):
        # Re-assign the real stdout/stderr back to (1) and (2)
        os.dup2(self.save_fds[0], 1)
        os.dup2(self.save_fds[1], 2)
        # Close all file descriptors
        for fd in self.null_fds + self.save_fds:
            os.close(fd)


def transform_date(date):
    unix_timestamp = int(978307200) * 1000000000  # "978307200" = "2001-01-01 00:00:00 UTC"
    new_date = int((date + unix_timestamp) / 1000000000)

    return new_date


def get_message(db_file, sql):
    start_time = int(datetime.datetime.now().timestamp())
    while True:
        messages = custom_sql.query(db_file, sql)
        if transform_date(messages[0][2]) > start_time:
            return messages[0][0], messages[0][3]
        else:
            time.sleep(1)


def dispatch_reply(gen_function, model_path, contact, prompt):
    print(f"Received from {contact}: {prompt}")
    with suppress_stdout_stderr():
        reply = gen_function(prompt, model_path)
    send_message(contact, reply)


def send_message(contact, message):
    message = message.replace("'", "")
    os.system(f"osascript send_message.scpt '{contact}' '{message}'")
    print(f"Sent to {contact}: {message}")


def monitor(gen_function, model_path, db_file, sql):
    print("Monitoring...")
    while True:
        contact, message = get_message(db_file, sql)
        # TODO: Add optional delay to wait for multiple messages
        multiprocessing.Process(target=dispatch_reply, args=(gen_function, model_path, contact, message)).start()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("model_type", choices=["gpt", "llama"], help="type of model to use")
    parser.add_argument("model_path", type=str, help="path/to/model.pt(h)")
    args = parser.parse_args()

    if args.model_type == "gpt":
        gen_function = generate.gpt.gen
    elif args.model_type == "llama":
        gen_function = generate.llama.gen
    else:
        raise ValueError("Invalid model type: {}".format(args.model_type))

    db_file = os.path.expanduser("~/Library/Messages/chat.db")
    with open("sql/new_messages.sql", "r") as sql_file:
        sql = sql_file.read().replace("\\n", "\n")

    monitor(gen_function, args.model_path, db_file, sql)


if __name__ == "__main__":
    main()
