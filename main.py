from telegram.ext import (MessageHandler,
                          CommandHandler,
                          Updater,
                          ConversationHandler,
                          CallbackQueryHandler,
                          Filters)
from keys import API_TOKEN
from callbacks.starter import start
from constants import *
from error_send import error_handler
from callbacks.language import greet_user
from text import buttons


def stringify(button_texts: str):
    list_of_buttons = []

    for i in buttons[button_texts]:
        list_of_buttons.append(buttons[button_texts][i])

    return list_of_buttons


def main():
    updater = Updater(token=API_TOKEN)
    dispatcher = updater.dispatcher

    main_conversation = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            LANGUAGE: [
                CallbackQueryHandler(greet_user),
                MessageHandler(Filters.regex("^(" + '|'.join(stringify('language')) + ")$"), greet_user)
            ]
        },
        fallbacks=[]
    )

    dispatcher.add_handler(main_conversation)
    dispatcher.add_error_handler(error_handler)

    updater.start_polling()
    updater.idle()
