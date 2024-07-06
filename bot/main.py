import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from utils.db import init_db

# Инициализация базы данных
init_db()

# Загрузка переменных окружения из файла .env
load_dotenv()

# Инициализация логирования
logging.basicConfig(level=logging.INFO)

# Получение токена бота из переменной окружения
API_TOKEN = os.getenv('API_TOKEN')

if not API_TOKEN:
    raise ValueError("No API token provided")

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Импортирование и включение роутеров
from handlers.user_handlers import router as user_router

dp.include_router(user_router)

if __name__ == '__main__':
    dp.run_polling(bot)