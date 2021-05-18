from telegram.ext import CallbackContext
from database_manager import get_chat, cursor, connect
from constants import NewUser, LANGUAGE, ActiveUser, MAIN_PAGE
from callbacks.newbie import choose_language
from callbacks.mainpage import main_menu


def start(update, context: CallbackContext):
    chat = get_chat(update)
    row = cursor.execute("SELECT id FROM users WHERE telegram_id = '{}'".format(chat)).fetchall()
    user = update.message

    if update.message.chat.id < 0:
        pass  # In Group

    else:
        if len(row) == 0:

            cursor.execute("""INSERT INTO users(
            id, telegram_id, name, username, phone_number, language, status) VALUES (
            NOT NULL, '{}', '{}', '{}', NULL, NULL, '{}')""".format(chat, user.from_user.full_name, user.from_user.username, NewUser))
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
                main_menu(update, context)
                return MAIN_PAGE


def reset(update, context):
    main_menu(update, context)
    return MAIN_PAGE

