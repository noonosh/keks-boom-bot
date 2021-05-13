from telegram.ext import CallbackContext
from telegram import (ReplyKeyboardMarkup,
                      KeyboardButton,
                      ReplyKeyboardRemove,
                      ParseMode,
                      InlineKeyboardButton,
                      InlineKeyboardMarkup)
from text import texts, buttons
from database_manager import cursor, connect, language, get_chat
from constants import LanguageGot


def choose_language(update, context):
    message = update.message
    btn = buttons['language']
    markup = [
        [InlineKeyboardButton(btn['uz'], callback_data='uz'),
         InlineKeyboardButton(btn['ru'], callback_data='ru'),
         InlineKeyboardButton(btn['en'], callback_data='en')]
    ]

    context.bot.send_message(chat_id=message.chat_id,
                             text=texts['choose_language'],
                             reply_markup=InlineKeyboardMarkup(markup),
                             parse_mode=ParseMode.MARKDOWN_V2)


def greet_user(update, context):
    # try-else block here allows us to ignore messages from user,
    # which are not CallbackQueryAnswers
    try:
        query = update.callback_query
        query.answer()
        cursor.execute("UPDATE users SET language = '{}', status = '{}' WHERE telegram_id = '{}'".format(
            query.data, LanguageGot, get_chat(update)))
        connect.commit()
        query.delete_message()
        context.bot.send_message(chat_id=get_chat(update),
                                 text=texts['greeting'][language(update)],
                                 parse_mode='HTML')
    except AttributeError:
        print('error')
        return
