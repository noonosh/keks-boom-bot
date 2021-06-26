
def instructions(update, context):
    chat_id = update.effective_chat.id
    context.bot.send_video(chat_id,
                           video="BAACAgIAAxkBAAIFBWDW_4KPRWFPBfdBvZvYN3tjaTnuAAK9DAACGVC4SlxU_LmBlQv8IAQ",
                           caption="🔥 Спасибо, что заинтересовались продуктом <b>«KEKS-BOOM»</b>\n\n"
                                   "📺 Просмотрите видео-инструкцию по использованию Кекс-Огней",
                           parse_mode="HTML")
