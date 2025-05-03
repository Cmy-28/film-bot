
import logging
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler

# Ключи
TMDB_API_KEY = '0756ce3fb98b8abc1f7ae98b8d09c908'
TELEGRAM_TOKEN = '7228118637:AAEpaWASF2G-BTmfM78pBwo5z94iFF5mmLQ'  # @Podborfilms_bot

logging.basicConfig(level=logging.INFO)

# Этапы диалога
GENRE, MOOD, PERSON, ERA, PLATFORM = range(5)

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [['Комедия', 'Триллер', 'Фантастика', 'Драма']]
    await update.message.reply_text(
        "Привет! Я — @Podborfilms_bot и помогу тебе найти фильм.\n\n"
        "1. Какой жанр вас сегодня привлекает?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return GENRE

async def genre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data['genre'] = update.message.text
    reply_keyboard = [['Расслабиться', 'Посмеяться'], ['Погрузиться в размышления']]
    await update.message.reply_text(
        "2. Какое настроение вы хотите поддержать или изменить?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return MOOD

async def mood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data['mood'] = update.message.text
    await update.message.reply_text("3. Есть ли любимые актёры, режиссёры или студии?")
    return PERSON

async def person(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data['person'] = update.message.text
    reply_keyboard = [['Новинки', 'Классика', 'Культовое кино 90-х']]
    await update.message.reply_text(
        "4. Хотите что-то новое или классику?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return ERA

async def era(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data['era'] = update.message.text
    reply_keyboard = [['Кинопоиск', 'YouTube'], ['Ivi', 'Okko']]
    await update.message.reply_text(
        "5. На какой платформе планируете смотреть?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return PLATFORM

async def platform(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data['platform'] = update.message.text

    genre = user_data['genre']
    genre_id = {
        'Комедия': 35, 'Триллер': 53, 'Фантастика': 878,
        'Драма': 18
    }.get(genre, 18)

    url = f'https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&with_genres={genre_id}&sort_by=popularity.desc'
    response = requests.get(url).json()
    movies = response.get('results', [])[:5]

    if not movies:
        await update.message.reply_text("К сожалению, не нашёл ничего подходящего.")
    else:
        reply = "Вот 5 фильмов для тебя:\n\n"
        for movie in movies:
            reply += f"• {movie['title']} ({movie['release_date'][:4]})\n"

        await update.message.reply_text(reply)

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Поиск отменён.")
    return ConversationHandler.END

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            GENRE: [MessageHandler(filters.TEXT & ~filters.COMMAND, genre)],
            MOOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, mood)],
            PERSON: [MessageHandler(filters.TEXT & ~filters.COMMAND, person)],
            ERA: [MessageHandler(filters.TEXT & ~filters.COMMAND, era)],
            PLATFORM: [MessageHandler(filters.TEXT & ~filters.COMMAND, platform)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()
