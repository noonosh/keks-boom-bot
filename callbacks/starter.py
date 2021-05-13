from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import CallbackContext
from database_manager import get_chat, cursor, connect
from constants import NewUser, LANGUAGE, ActiveUser
from callbacks.language import choose_language


def start(update, context: CallbackContext):
    chat = get_chat(update)
    row = cursor.execute("SELECT id FROM users WHERE telegram_id = '{}'".format(chat)).fetchall()
    user = update.message.from_user

    if chat < 0:
        return  # In Group

    else:
        if len(row) == 0:

            cursor.execute("""INSERT INTO users(
            id, telegram_id, name, username, phone_number, language, status) VALUES (
            NOT NULL, '{}', '{}', '{}', NULL, NULL, '{}')""".format(chat, user.full_name, user.username, NewUser))
            connect.commit()

            choose_language(update, context)
            return LANGUAGE
        else:
            status = cursor.execute("SELECT status FROM users where telegram_id = '{}'"
                                    .format(chat)).fetchone()[0]
            if status != ActiveUser:
                cursor.execute("DELETE FROM users WHERE telegram_id = '{}'"
                               .format(chat))
                connect.commit()
                start(update, context)
                return LANGUAGE
            else:
                pass


