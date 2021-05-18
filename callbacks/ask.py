from database_manager import get_chat, language, cursor
from telegram import ReplyKeyboardMarkup
from configurations import RESPONSES_GROUP_ID
from text import buttons, texts
from constants import ASKING, MAIN_PAGE
from callbacks.mainpage import back_to_main


def ask_me(update, context):
    btn = [
        [buttons['back'][language(update)]]
    ]
    context.bot.send_message(chat_id=get_chat(update),
                             text=texts['ask_me'][language(update)],
                             reply_markup=ReplyKeyboardMarkup(btn, resize_keyboard=True))
    return ASKING


def forward_message(update, context):
    message_id = update.effective_message.message_id
    chat_id = update.effective_message.chat_id

    msg = context.bot.forward_message(chat_id=RESPONSES_GROUP_ID,
                                      from_chat_id=chat_id,
                                      message_id=message_id)

    payload = {
        msg.message_id: chat_id
    }
    context.bot_data.update(payload)

    update.effective_message.reply_text(texts['got_you'][language(update)])
    back_to_main(update, context)
    return MAIN_PAGE


def reply_to_message(update, context):
    try:
        if update.message.reply_to_message:
            response = update.message.text
            reply_id = update.message.reply_to_message.message_id
            user_id = context.bot_data[reply_id]
            lang = cursor.execute("SELECT language FROM Users WHERE telegram_id = '{}'"
                                  .format(user_id)).fetchone()[0]
            reply = texts['replying'][lang].format(response)
            context.bot.send_message(chat_id=user_id,
                                     text=reply,
                                     parse_mode='HTML')
        else:
            pass
    except KeyError:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='На это ответить я не могу 😢\n'
                                      'Выберите реальный запрос который я вам отправил')
