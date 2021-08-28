from utils.text import texts
from utils.database_manager import language


def instructions(update, context):
    chat_id = update.effective_chat.id
    context.bot.send_video(chat_id,
                           video="BAACAgIAAxkBAAIFBWDW_4KPRWFPBfdBvZvYN3tjaTnuAAK9DAACGVC4SlxU_LmBlQv8IAQ",
                           caption=texts['video_caption'][language(update)],
                           parse_mode="HTML")
