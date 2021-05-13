from telegram.ext import CallbackContext
from telegram import ReplyKeyboardMarkup, KeyboardButton, ParseMode
from text import texts, buttons
from database_manager import cursor, connect


def choose_language(update, context):
    message = update.message
    btn = buttons['language']
    markup = [
        [KeyboardButton(btn['uz']),
         KeyboardButton(btn['ru'])],
        [KeyboardButton(btn['en'])]
    ]

    context.bot.send_message(chat_id=message.chat_id,
                             text=texts['choose_language'],
                             reply_markup=ReplyKeyboardMarkup(markup),
                             parse_mode=ParseMode.MARKDOWN_V2)


def greet_user(update, context):
    # try-else block here allows us to ignore messages from user,
    # which are not CallbackQueryAnswers

    update.message.reply_text(update.message.text)
