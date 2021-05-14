from telegram.ext import (MessageHandler,
                          CommandHandler,
                          Updater,
                          ConversationHandler,
                          CallbackQueryHandler,
                          Filters)
from keys import API_TOKEN
from callbacks.starter import start, reset
from constants import *
from error_send import error_handler
from callbacks.newbie import greet_user, name_accept
from callbacks.settings import change_language
from callbacks.orders import preview
from text import buttons
from callbacks.settings import settings_markup, change_language


def stringify(button_texts: str):
    list_of_buttons = []

    for i in buttons[button_texts]:
        list_of_buttons.append(buttons[button_texts][i])

    return list_of_buttons


def ignore(update, context):
    print('ignored!')
    return


def main():
    updater = Updater(token=API_TOKEN)
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
                MessageHandler(Filters.regex('^' + '|'.join(stringify('order')) + '$'), preview),
                MessageHandler(Filters.regex('^' + '|'.join(stringify('watch_tutorial')) + '$'), ignore),
                MessageHandler(Filters.regex('^' + '|'.join(stringify('ask_question')) + '$'), ignore),
                MessageHandler(Filters.regex('^' + '|'.join(stringify('change_language')) + '$'), settings_markup)
            ],
            CHANGING_LANG: [
                MessageHandler(Filters.regex('^' + '|'.join(stringify('language')) + '$'), change_language)
            ]
        },
        fallbacks=[
            MessageHandler(Filters.all, reset)
        ]
    )

    dispatcher.add_handler(main_conversation)
    dispatcher.add_error_handler(error_handler)

    updater.start_polling()
    updater.idle()
