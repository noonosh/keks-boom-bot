from telegram.ext import CallbackContext
from telegram import (ParseMode,
                      InlineKeyboardButton,
                      InlineKeyboardMarkup)
from text import texts, buttons
from database_manager import cursor, connect, language, get_chat
from constants import LanguageGot, NAME, MAIN_PAGE, ActiveUser
from callbacks.mainpage import main_menu


def choose_language(update, context):
    message = update.message
    btn = buttons['language']
    markup = [
        [InlineKeyboardButton(btn['uz'], callback_data='uz'),
         InlineKeyboardButton(btn['ru'], callback_data='ru'),
         InlineKeyboardButton(btn['en'], callback_data='en')]
    ]
    try:
        context.bot.delete_message(chat_id=get_chat(update),
                                   message_id=context.chat_data['language_message_id'])

        msg = context.bot.send_message(chat_id=message.chat_id,
                                       text=texts['choose_language'],
                                       reply_markup=InlineKeyboardMarkup(markup),
                                       parse_mode=ParseMode.MARKDOWN_V2)
        context.chat_data.update({
            'language_message_id': msg.message_id
        })
    except KeyError:
        msg = context.bot.send_message(chat_id=message.chat_id,
                                       text=texts['choose_language'],
                                       reply_markup=InlineKeyboardMarkup(markup),
                                       parse_mode=ParseMode.MARKDOWN_V2)
        context.chat_data.update({
            'language_message_id': msg.message_id
        })


def greet_user(update, context):
    query = update.callback_query
    query.answer()

    cursor.execute("UPDATE users SET language = '{}', status = '{}' WHERE telegram_id = '{}'"
                   .format(query.data, LanguageGot, get_chat(update)))
    connect.commit()

    query.delete_message()
    context.bot.send_message(chat_id=get_chat(update),
                             text=texts['greeting'][language(update)],
                             parse_mode='HTML')
    return NAME


def name_accept(update, context: CallbackContext):
    message = update.effective_message
    a = message.text.split()

    if len(a) == 1 and a[0][0].isupper():
        cursor.execute("UPDATE users SET name = '{}', status = '{}' WHERE telegram_id = '{}'"
                       .format(message.text, ActiveUser, get_chat(update)))
        connect.commit()

        context.bot.send_message(chat_id=get_chat(update),
                                 text=texts['name_accepted'][language(update)].format(message.text))

        main_menu(update, context)
        return MAIN_PAGE
    else:
        update.effective_message.reply_text(texts['name_error'][language(update)],
                                            parse_mode='HTML')
