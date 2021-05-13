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

new_string = '|'.join(buttons['language']['uz'])
print(new_string)


def main():
    updater = Updater(token=API_TOKEN)
    dispatcher = updater.dispatcher

    main_conversation = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            LANGUAGE: [
                MessageHandler(Filters.regex('^' + new_string + '$'), greet_user)
            ]
        },
        fallbacks=[]
    )

    dispatcher.add_handler(main_conversation)
    dispatcher.add_error_handler(error_handler)

    updater.start_polling()
    updater.idle()
