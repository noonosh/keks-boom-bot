import pandas as pd
from telegram.ext import CallbackContext
from database_manager import get_chat, connect, cursor
import datetime
from functools import wraps


def restricted(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        a = cursor.execute("SELECT telegram_id FROM admins"
                           .format(user_id)).fetchall()
        IS_ADMIN = []
        for i in a:
            IS_ADMIN.append(i[0])
        if user_id not in IS_ADMIN:
            print("Unauthorized access denied for {}.".format(user_id))
            return
        return func(update, context, *args, **kwargs)

    return wrapped


@restricted
def export(update, context: CallbackContext):
    db_df = pd.read_sql_query("SELECT * FROM users", connect)
    db_df.to_csv(f'exports/export_{datetime.date.today()}.csv')
    context.bot.send_document(chat_id=get_chat(update),
                              document=open(f'exports/export_{datetime.date.today()}.csv'))
