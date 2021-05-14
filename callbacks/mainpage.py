from telegram.ext import CallbackContext
from telegram import ReplyKeyboardMarkup, KeyboardButton
from text import texts, buttons
from database_manager import language, get_chat


def main_menu(update, context: CallbackContext):
    markup = [
        [KeyboardButton(buttons['order'][language(update)])],
        [KeyboardButton(buttons['watch_tutorial'][language(update)]),
         KeyboardButton(buttons['ask_question'][language(update)])],
        [KeyboardButton(buttons['change_language'][language(update)])]
    ]

    context.bot.send_message(chat_id=get_chat(update),
                             text=texts['main_menu'][language(update)],
                             reply_markup=ReplyKeyboardMarkup(markup, resize_keyboard=True))


