import logging
import sqlite3
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware


chat_id = 0
API_TOKEN = '6080476467:AAGPcsiW4Q-uJe5F_s3MA9tqOQgjzbQ9BAk'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    conn = sqlite3.connect('Data.db')
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM users WHERE id={message.from_user.id}")
    if len(cur.fetchall()) == 0:
        cur.execute(f"""INSERT INTO users  VALUES ({message.from_user.id})""")
        conn.commit()
        conn.close()
        await message.answer('Успешно')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
