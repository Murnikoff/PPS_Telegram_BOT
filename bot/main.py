import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from utils.db import init_db
from handlers.command_handlers import command_router
from handlers.callback_handlers import callback_router

init_db()
load_dotenv()
logging.basicConfig(level=logging.INFO)

API_TOKEN = os.getenv('API_TOKEN')

if not API_TOKEN:
    raise ValueError("No API token provided")

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

dp.include_router(command_router)
dp.include_router(callback_router)

if __name__ == '__main__':
    dp.run_polling(bot)