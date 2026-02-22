import asyncio
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    filters, 
    CallbackQueryHandler, 
    ContextTypes
)
import logging
from urllib.parse import quote

# ========== КОНФИГУРАЦИЯ ==========
TELEGRAM_TOKEN = "8320964331:AAG4SLVhgQ_fCLehp01e-_jWz6FqBka5H4k"
KINOPOISK_TOKEN = "1e319d29-42d7-4ada-b092-208ba949febb"  # Получите на https://kinopoiskapiunofficial.tech/

# ========== НАСТРОЙКА ЛОГИРОВАНИЯ ==========
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== КЛАСС ДЛЯ РАБОТЫ С КИНОПОИСКОМ (ПРАВИЛЬНЫЙ API) ==========
class KinopoiskAPI:
    def __init__(self, api_key):
        self.headers = {
            "X-API-KEY": api_key,
            "Content-Type": "application/json"
        }
        self.base_url = "https://kinopoiskapiunofficial.tech/api/v2.2"
    
    def search_movie(self, title, year=None):
        """Поиск фильмов по названию - ЭТО ПРАВИЛЬНЫЙ МЕТОД!"""
        try:
            # Кодируем название для URL
            encoded_title = quote(title)
            url = f"{self.base_url}/films"
            
            params = {
                "keyword": title,
                "page": 1
            }
            
            logger.info(f"Ищу фильм: {title}")
            
            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            logger.info(f"Статус ответа: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                films = data.get("items", [])
                logger.info(f"Найдено фильмов: {len(films)}")
                
                # Фильтруем по году если указан
                if year and films:
                    films = [f for f in films if f.get('year') == str(year)]
                
                return films[:5]  # Возвращаем первые 5 результатов
            else:
                logger.error(f"Ошибка API: {response.status_code}, текст: {response.text}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса: {e}")
            return []
        except Exception as e:
            logger.error(f"Неизвестная ошибка: {e}")
            return []
    
    def get_movie_details(self, movie_id):
        """Получение деталей фильма по ID - ТОЧНО РАБОТАЕТ!"""
        try:
            url = f"{self.base_url}/films/{movie_id}"
            logger.info(f"Запрашиваю детали фильма ID: {movie_id}")
            
            response = requests.get(
                url,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Ошибка получения деталей: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка получения деталей фильма: {e}")
            return None
    
    def get_movie_videos(self, movie_id):
        """Получение видео (трейлеров) для фильма"""
        try:
            url = f"{self.base_url}/films/{movie_id}/videos"
            
            response = requests.get(
                url,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("items", [])
            return []
            
        except Exception as e:
            logger.error(f"Ошибка получения видео: {e}")
            return []

# ========== ИНИЦИАЛИЗАЦИЯ API ==========
kp_api = KinopoiskAPI(KINOPOISK_TOKEN)

# ========== КОМАНДЫ БОТА ==========
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    user = update.effective_user
    
    welcome_text = f"""
🎬 Привет, {user.first_name}! Я бот для поиска фильмов.

Как пользоваться:
1. Просто напиши название фильма на РУССКОМ или АНГЛИЙСКОМ
2. Укажи год при необходимости
3. Выбери фильм из списка
4. Получи ссылки на трейлеры

Примеры запросов:
• интерстеллар
• матрица 1999
• titanic
• harry potter 2001
• лесной житель 2022

Напиши название фильма или используй /search
    """
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /search"""
    if context.args:
        query = " ".join(context.args)
        await search_movies(update, query)
    else:
        await update.message.reply_text(
            "🔍 *Как искать фильмы:*\n\n"
            "1. Просто напиши название\n"
            "2. Можно добавить год\n"
            "3. Можно на русском или английском\n\n"
            "*Пример:*\n`матрица` или `titanic 1997`",
            parse_mode='Markdown'
        )

async def search_movies(update: Update, query: str) -> None:
    """Поиск фильмов"""
    await update.message.reply_text(f"🔍 Ищу *{query}*...", parse_mode='Markdown')
    
    # Парсим год из запроса
    parts = query.split()
    year = None
    title_parts = []
    
    for part in parts:
        if part.isdigit() and len(part) == 4 and 1900 <= int(part) <= 2100:
            year = int(part)
        else:
            title_parts.append(part)
    
    title = " ".join(title_parts).strip()
    
    if not title:
        await update.message.reply_text("❌ Пожалуйста, укажите название фильма.")
        return
    
    # Выполняем поиск
    movies = kp_api.search_movie(title, year)
    
    if not movies:
        if year:
            await update.message.reply_text(
                f"❌ Фильм *{title}* ({year} год) не найден.\n\n"
                "💡 *Советы:*\n"
                "1. Проверьте правильность написания\n"
                "2. Попробуйте английское название\n"
                "3. Попробуйте без года",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                f"❌ Фильм *{title}* не найден.\n\n"
                "💡 *Советы:*\n"
                "1. Попробуйте другое название\n"
                "2. Используйте оригинальное название\n"
                "3. Укажите год выпуска",
                parse_mode='Markdown'
            )
        return
    
    # Создаем клавиатуру с результатами
    keyboard = []
    for movie in movies:
        movie_title = movie.get('nameRu') or movie.get('nameEn') or 'Без названия'
        movie_year = movie.get('year', '')
        
        # Рейтинг если есть
        rating = ""
        if movie.get('rating'):
            rating = f" ⭐{movie['rating']}"
        
        # Форматируем текст кнопки
        if len(movie_title) > 25:
            display_title = movie_title[:22] + "..."
        else:
            display_title = movie_title
        
        btn_text = f"{display_title} ({movie_year}){rating}"
        callback_data = f"movie_{movie['kinopoiskId']}"
        
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=callback_data)])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🎯 *Найдено фильмов:* {len(movies)}\nВыберите нужный:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик текстовых сообщений"""
    if update.message.text.startswith('/'):
        return
    
    await search_movies(update, update.message.text)

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("movie_"):
        movie_id = query.data.split("_")[1]
        await show_movie_details(update, context, movie_id)
    elif query.data == "new_search":
        await query.edit_message_text(
            "🔍 *Введите название фильма для поиска:*\n\n"
            "*Примеры:*\n"
            "• брат\n"
            "• лесной житель\n"
            "• avatar 2009",
            parse_mode='Markdown'
        )

async def show_movie_details(update: Update, context: ContextTypes.DEFAULT_TYPE, movie_id: str) -> None:
    """Показать детали фильма и ссылки"""
    query = update.callback_query
    
    await query.edit_message_text("📡 Загружаю информацию о фильме...")
    
    # Получаем данные фильма
    movie_data = kp_api.get_movie_details(movie_id)
    
    if not movie_data:
        await query.edit_message_text("❌ Не удалось загрузить информацию о фильме.")
        return
    
    # Получаем видео
    videos = kp_api.get_movie_videos(movie_id)
    
    # Извлекаем информацию
    name_ru = movie_data.get("nameRu", "")
    name_en = movie_data.get("nameEn", "")
    year = movie_data.get("year", "")
    description = movie_data.get("description", "")
    rating = movie_data.get("ratingKinopoisk", "")
    
    if description and len(description) > 400:
        description = description[:400] + "..."
    
    # Формируем сообщение
    message = "🎬 "
    if name_ru:
        message += f"*{name_ru}*"
        if name_en and name_en.lower() != name_ru.lower():
            message += f"\n({name_en})"
    elif name_en:
        message += f"*{name_en}*"
    else:
        message += "*Неизвестный фильм*"
    
    if year:
        message += f" ({year})"
    
    if rating:
        message += f"\n⭐ Рейтинг: *{rating}*"
    
    message += "\n\n"
    
    if description:
        message += f"*Описание:* {description}\n\n"
    
    message += "*🔗 Ссылки:*\n"
    
    # Основная ссылка на Кинопоиск
    message += f"• [📝 Страница на Кинопоиске](https://www.kinopoisk.ru/film/{movie_id}/)\n"
    
    # Ссылка на трейлеры с YouTube
    youtube_trailers = []
    other_trailers = []
    
    for video in videos:
        if video.get("site") == "YOUTUBE" and video.get("url"):
            youtube_trailers.append(video)
        elif video.get("url"):
            other_trailers.append(video)
    
    # Добавляем YouTube трейлеры (первые 3)
    for i, trailer in enumerate(youtube_trailers[:3], 1):
        trailer_name = trailer.get("name", f"Трейлер {i}")
        message += f"• [🎬 {trailer_name}]({trailer['url']})\n"
    
    # Если нет YouTube, добавляем другие видео
    if not youtube_trailers:
        for i, trailer in enumerate(other_trailers[:2], 1):
            trailer_name = trailer.get("name", f"Видео {i}")
            message += f"• [🎥 {trailer_name}]({trailer['url']})\n"
    
    # Если вообще нет видео
    if not youtube_trailers and not other_trailers:
        message += "• 🎬 Трейлеры не найдены\n"
    
    # Ссылка на поиск в Google
    #search_query = name_ru or name_en
    #if search_query:
        #google_search = quote(f"{search_query} {year} смотреть онлайн")
        #message += f"• [🌐 Искать в Google](https://www.google.com/search?q={google_search})\n"

    #  ссылка на Плеер 1
    message += f"• [🎥 Плеер 1](https://www.sspoisk.ru/film/{movie_id}/)\n"    
    message += f"• [🎥 Плеер 2](https://www.kinopoisk.gg/film/{movie_id}/)\n" 
    # Создаем кнопки для навигации
    keyboard = [
        [InlineKeyboardButton("🔍 Новый поиск", callback_data="new_search")]
        #[InlineKeyboardButton("📺 Еще фильмы", callback_data="more_movies")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown',
            disable_web_page_preview=False  # Разрешаем превью для YouTube
        )
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        # Отправляем новое сообщение если не удалось отредактировать
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text=message,
            parse_mode='Markdown',
            disable_web_page_preview=False
        )

# ========== ОСНОВНАЯ ФУНКЦИЯ ==========
def main() -> None:
    """Запуск бота"""
    # Создаем Application
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("search", search_command))
    
    # Регистрируем обработчик кнопок
    application.add_handler(CallbackQueryHandler(handle_button))
    
    """keyboard = [InlineKeyboardButton("Кнопка 1", callback_data='button1'), InlineKeyboardButton("Кнопка 2", callback_data='button2')] ].
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Выберите опцию:', reply_markup=reply_markup).
    Обработчик нажатий на кнопку:
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):.
query = update.callback_query.
await query.answer().
await query.edit_message_text(text=f"Вы нажали: {query.data}").
Регистрация обработчика:
app = ApplicationBuilder().token("ВАШ_ТОКЕН_ЗДЕСЬ").build().
app.add_handler(CallbackQueryHandler(button_handler))."""
    # Регистрируем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Запускаем бота
    print("=" * 50)
    print("🎬 Movie Finder Bot запущен!")
    print("API: kinopoiskapiunofficial.tech")
    print("=" * 50)
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()