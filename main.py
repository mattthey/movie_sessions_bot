import logging
import os

from telegram import InputMediaPhoto
from telegram._inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram._inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram._update import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler

from movie_sessions import get_pretty_films, FILMS

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def get_buttons(current_position=0):
    result = []
    if current_position > 0:
        result.append(InlineKeyboardButton(
            text="Назад", callback_data=str(current_position - 1)))
    if current_position < len(FILMS):
        result.append(InlineKeyboardButton(
            text="Далее", callback_data=str(current_position + 1)))
    return result


async def start(update: Update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Отправь /sessions")


async def sessions(update: Update, context):
    with open('media/0', 'rb') as photo:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=photo,
            caption=get_pretty_films(),
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup.from_row(get_buttons())
        )


async def list_button(update: Update, context) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    await query.answer()
    id = int(query.data)

    with open('media/' + str(id), 'rb') as f:
        imp = InputMediaPhoto(f, get_pretty_films(id), ParseMode.HTML)
        await query.edit_message_media(
            media=imp,
            reply_markup=InlineKeyboardMarkup.from_row(get_buttons(id))
        )
    context.drop_callback_data(query)


if __name__ == '__main__':
    application = ApplicationBuilder() \
        .token(os.getenv('bot_token')) \
        .arbitrary_callback_data(True) \
        .build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    sessions_handler = CommandHandler('sessions', sessions)
    application.add_handler(sessions_handler)

    application.add_handler(CallbackQueryHandler(list_button))

    application.run_polling()
