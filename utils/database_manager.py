import sqlite3

path = 'database.sqlite'

connect = sqlite3.connect(path, check_same_thread=False)

cursor = connect.cursor()


def get_chat(update):
    return update.effective_chat.id


def language(update):
    return cursor.execute("SELECT language FROM users WHERE telegram_id = '{}'"
                          .format(get_chat(update))).fetchone()[0]
