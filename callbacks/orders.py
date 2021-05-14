from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import CallbackContext
from database_manager import get_chat
from constants import SELECTING_QUANTITY


def preview(update, context: CallbackContext):
    context.bot.send_photo(chat_id=get_chat(update),
                           photo=open('./assets/boom.jpg', 'rb'),
                           caption='this is a caption')
    quantity(update, context)
    return SELECTING_QUANTITY


def quantity(update, context):
    update.effective_message.reply_text('please choose a quantity for this item')
