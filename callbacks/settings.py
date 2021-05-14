from telegram import KeyboardButton, ReplyKeyboardMarkup
from database_manager import *
from text import buttons, texts
from constants import CHANGING_LANG, MAIN_PAGE
from callbacks.mainpage import main_menu


def settings_markup(update, context):
    markup = [
        [KeyboardButton(buttons['language']['uz']), KeyboardButton(buttons['language']['ru'])],
        [KeyboardButton(buttons['language']['en'])],
        [KeyboardButton(buttons['back'][language(update)])]
    ]

    context.bot.send_message(chat_id=get_chat(update),
                             text=texts['change_language'][language(update)],
                             reply_markup=ReplyKeyboardMarkup(markup, resize_keyboard=True))
    return CHANGING_LANG


def change_language(update, context):
    choice = update.message.text
    if choice == buttons['language']['ru']:
        cursor.execute(
            "UPDATE Users SET language = 'ru' WHERE telegram_id = '{}'".format(get_chat(update)))
        connect.commit()
    if choice == buttons['language']['uz']:
        cursor.execute(
            "UPDATE Users SET language = 'uz' WHERE telegram_id = '{}'".format(get_chat(update)))
        connect.commit()
    if choice == buttons['language']['en']:
        cursor.execute(
            "UPDATE Users SET language = 'en' WHERE telegram_id = '{}'".format(get_chat(update)))
        connect.commit()
    context.bot.send_message(chat_id=get_chat(update),
                             text=texts['done'][language(update)])
    done(update, context)
    return MAIN_PAGE


def done(update, context):
    main_menu(update, context)

