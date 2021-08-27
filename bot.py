from telegram.ext import (MessageHandler,
                          CommandHandler,
                          Updater,
                          ConversationHandler,
                          CallbackQueryHandler,
                          Filters, PicklePersistence)
from ptbcontrib.reply_to_message_filter import ReplyToMessageFilter
from callbacks.starter import start
from utils.constants import *
from utils.error_send import error_handler
from callbacks.newbie import greet_user, name_accept
from callbacks.orders import (preview, get_quantity, check_phone, address, request_phone, request_address,
                              get_comments, checkout, cancel_order, confirm_order)
from utils.text import buttons
from callbacks.settings import settings_markup, change_language
from callbacks.mainpage import back_to_main
from callbacks.ask import ask_me, forward_message, reply_to_message
from callbacks.export_db import export
from callbacks.how_to_use import instructions
import os
import dotenv

dotenv.load_dotenv()


def stringify(button_texts: str):
    list_of_buttons = []

    for i in buttons[button_texts]:
        list_of_buttons.append(buttons[button_texts][i])

    return list_of_buttons


def ignore(update, context):
    print('ignored!')
    return


def join_regex(param: str):
    return '^' + '|'.join(stringify(param)) + '$'


def back_button():
    return join_regex('back')


def main():
    my_persistence = PicklePersistence(filename='RESTRICTED')
    updater = Updater(token=os.getenv("BOT_TOKEN"), persistence=my_persistence)
    dispatcher = updater.dispatcher

    main_conversation = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            LANGUAGE: [
                CallbackQueryHandler(greet_user)
            ],
            NAME: [
                MessageHandler(Filters.text, name_accept)
            ],
            MAIN_PAGE: [
                MessageHandler(Filters.regex(join_regex('order')), preview),
                MessageHandler(Filters.regex(
                    join_regex('watch_tutorial')), instructions),
                MessageHandler(Filters.regex(
                    join_regex('ask_question')), ask_me),
                MessageHandler(Filters.regex(join_regex(
                    'change_language')), settings_markup)
            ],
            CHANGING_LANG: [
                MessageHandler(Filters.regex(
                    join_regex('language')), change_language),
                CommandHandler('download', export)
            ],
            ASKING: [
                MessageHandler(Filters.regex(back_button()), back_to_main),
                MessageHandler(Filters.text | Filters.photo | Filters.video | Filters.document,
                               forward_message)
            ],
            SELECTING_QUANTITY: [
                MessageHandler(Filters.regex(back_button()), back_to_main),
                MessageHandler(Filters.text, get_quantity)
            ],
            REQUESTING_PHONE: [
                MessageHandler(Filters.regex(back_button()), preview),
                MessageHandler(Filters.contact | Filters.text, check_phone)
            ],
            REQUESTING_ADDRESS: [
                MessageHandler(Filters.regex(back_button()), request_phone),
                MessageHandler(Filters.location, address)
            ],
            REQUESTING_COMMENTS: [
                MessageHandler(Filters.regex(back_button()), request_address),
                MessageHandler(Filters.regex(join_regex('skip')), checkout),
                MessageHandler(Filters.text, get_comments)
            ],
            CONFIRMING_ORDER: [
                MessageHandler(Filters.regex(
                    join_regex('confirm')), confirm_order),
                MessageHandler(Filters.regex(
                    join_regex('cancel')), cancel_order)
            ]
        },
        fallbacks=[
            MessageHandler(Filters.all & (~ Filters.user(1644589072)), start)
        ],
        name='main_conv',
        persistent=True
    )

    dispatcher.add_handler(main_conversation)
    dispatcher.add_error_handler(error_handler)
    dispatcher.add_handler(MessageHandler(ReplyToMessageFilter(
        Filters.user(1644589072)), reply_to_message))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
