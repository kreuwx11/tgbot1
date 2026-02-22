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
KINOPOISK_TOKEN = "1e319d29-42d7-4ada-b092-208ba949febb"

# ========== НАСТРОЙКА ЛОГИРОВАНИЯ ==========
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== КЛАСС ДЛЯ РАБОТЫ С КИНОПОИСКОМ ==========
'''class KinopoiskAPI:
    def __init__(self, api_key):
        self.headers = {"X-API-KEY": '1e319d29-42d7-4ada-b092-208ba949febb'}
        self.base_url = "https://api.kinopoisk.dev/v2.2/movie"
    
    def search_movie(self, title, year=None):
        """Поиск фильмов по названию"""
        params = {
            "query": title,
            "limit": 5,
            "selectFields": ["id", "name", "year", "rating", "poster"]
        }
        
        if year:
            params["year"] = str(year)
        
        try:
            response = requests.get(
                f"{self.base_url}/search",
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Найдено фильмов: {len(data.get('docs', []))}")
                return data.get("docs", [])
            else:
                logger.error(f"Ошибка API: {response.status_code}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса: {e}")
            return []
        except Exception as e:
            logger.error(f"Неизвестная ошибка: {e}")
            return []
    
    def get_movie_details(self, movie_id):
        """Получение деталей фильма и ссылок"""
        try:
            response = requests.get(
                f"{self.base_url}/{movie_id}",
                headers=self.headers,
                params={
                    "selectFields": ["name", "year", "videos", "externalId", "description"]
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception as e:
            logger.error(f"Ошибка получения деталей фильма: {e}")
            return None
'''
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
1. Просто напиши название фильма
2. Укажи год при необходимости
3. Выбери фильм из списка
4. Получи ссылки на трейлеры и просмотр

Примеры:
• Интерстеллар
• Матрица 1999
• Титаник 1997

Напиши название фильма или используй /search
    """
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help"""
    help_text = """
Команды бота:
/start - Начало работы
/help - Эта справка
/search - Начать поиск

Формат запроса:
Просто отправь сообщение с названием фильма.
Можно указать год: "Интерстеллар 2014"

Что умеет бот:
• Искать фильмы по названию
• Уточнять поиск по году
• Показывать трейлеры
• Давать ссылки на Кинопоиск
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /search"""
    if context.args:
        query = " ".join(context.args)
        await search_movies(update, query)
    else:
        await update.message.reply_text(
            "🔍 Введите название фильма для поиска:\n"
            "Например: *Матрица 1999*",
            parse_mode='Markdown'
        )

async def search_movies(update: Update, query: str) -> None:
    """Поиск фильмов"""
    await update.message.reply_text("🔍 Ищу фильмы...")
    
    # Парсим год из запроса
    parts = query.split()
    year = None
    title_parts = []
    
    for part in parts:
        if part.isdigit() and len(part) == 4 and 1900 <= int(part) <= 2100:
            year = int(part)
        else:
            title_parts.append(part)
    
    title = " ".join(title_parts)
    
    if not title:
        await update.message.reply_text("❌ Пожалуйста, укажите название фильма.")
        return
    
    # Выполняем поиск
    movies = kp_api.search_movie(title, year)
    
    if not movies:
        if year:
            await update.message.reply_text(f"❌ Не найдено фильмов: {title} ({year} год)")
        else:
            await update.message.reply_text(f"❌ Не найдено фильмов: {title}")
        return
    
    # Создаем клавиатуру с результатами
    keyboard = []
    for movie in movies:
        movie_title = movie.get('name', 'Без названия')
        movie_year = movie.get('year', '')
        rating = movie.get('rating', {}).get('kp', '?')
        
        # Форматируем текст кнопки
        if len(movie_title) > 25:
            display_title = movie_title[:22] + "..."
        else:
            display_title = movie_title
        
        btn_text = f"{display_title} ({movie_year}) ⭐{rating}"
        callback_data = f"movie_{movie['id']}"
        
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=callback_data)])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🎯 *Найдено {len(movies)} фильмов:*\nВыберите нужный:",
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
        await query.edit_message_text("🔍 Введите название фильма для поиска:")

async def show_movie_details(update: Update, context: ContextTypes.DEFAULT_TYPE, movie_id: str) -> None:
    """Показать детали фильма и ссылки"""
    query = update.callback_query
    
    await query.edit_message_text("📡 Загружаю информацию о фильме...")
    
    # Получаем данные фильма
    movie_data = kp_api.get_movie_details(movie_id)
    
    if not movie_data:
        await query.edit_message_text("❌ Не удалось загрузить информацию о фильме.")
        return
    
    # Извлекаем информацию
    movie_name = movie_data.get("name", "Неизвестный фильм")
    movie_year = movie_data.get("year", "")
    description = movie_data.get("description", "")
    
    if description and len(description) > 300:
        description = description[:300] + "..."
    
    # Формируем сообщение
    message = f"🎬 *{movie_name}*"
    if movie_year:
        message += f" ({movie_year})"
    message += "\n\n"
    
    if description:
        message += f"*Описание:* {description}\n\n"
    
    message += "*🔗 Ссылки:*\n"
    
    # Ссылка на Кинопоиск
    message += f"• [Страница на Кинопоиске](https://www.kinopoisk.ru/film/{movie_id}/)\n"
    
    # Трейлеры
    if "videos" in movie_data and "trailers" in movie_data["videos"]:
        trailers = movie_data["videos"]["trailers"]
        for i, trailer in enumerate(trailers[:2], 1):  # Берем до 2 трейлеров
            if trailer.get("url"):
                trailer_name = trailer.get("name", f"Трейлер {i}")
                message += f"• [{trailer_name}]({trailer['url']})\n"
    
    # Ссылка на Kinopoisk HD если есть
    if "externalId" in movie_data and movie_data["externalId"].get("kpHD"):
        message += f"• [Смотреть на Кинопоиск HD](https://hd.kinopoisk.ru/film/{movie_data['externalId']['kpHD']})\n"
    
    # Создаем кнопки для навигации
    keyboard = [
        [InlineKeyboardButton("🔍 Новый поиск", callback_data="new_search")],
        [InlineKeyboardButton("🎬 Еще фильмы", callback_data="more_movies")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
    except Exception as e:
        logger.error(f"Ошибка редактирования сообщения: {e}")
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text=message,
            parse_mode='Markdown',
            disable_web_page_preview=True
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик ошибок"""
    logger.error(f"Ошибка: {context.error}", exc_info=context.error)
    
    if update:
        try:
            await update.effective_message.reply_text(
                "❌ Произошла ошибка. Пожалуйста, попробуйте еще раз."
            )
        except:
            pass

# ========== ОСНОВНАЯ ФУНКЦИЯ ==========
def main() -> None:
    """Запуск бота"""
    # Создаем Application
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("search", search_command))
    
    # Регистрируем обработчик кнопок
    application.add_handler(CallbackQueryHandler(handle_button))
    
    # Регистрируем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Регистрируем обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Запускаем бота
    print("=" * 50)
    print("🤖 Movie Finder Bot запущен!")
    print("Остановите бота нажатием Ctrl+C")
    print("=" * 50)
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()