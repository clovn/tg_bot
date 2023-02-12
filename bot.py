import logging
import sqlite3
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import FiltersFactory
from utils import Create_Task


API_TOKEN = '6080476467:AAGPcsiW4Q-uJe5F_s3MA9tqOQgjzbQ9BAk'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())


@dp.message_handler(commands=['start'], state="*")
async def send_welcome(message: types.Message, state:FSMContext):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Создать заявку'))
    await message.answer("HI", reply_markup=keyboard)


@dp.message_handler(text=['Создать заявку'], state="*")
async def send_welcome(message: types.Message, state: FSMContext):
    keyboard = InlineKeyboardMarkup()
    conn = sqlite3.connect('Data.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM autoservices")
    services = [list(i) for i in cur.fetchall()]
    for i in services:
        keyboard.add(InlineKeyboardButton(text=i[1], callback_data=f"service_button;{i[0]}"))
    await message.answer("Выберите сервис", reply_markup=keyboard)
    await state.set_state(Create_Task.create)


@dp.callback_query_handler(lambda c: c.data.startswith('service_button'), state=Create_Task.create)
async def process_callback_kb1btn1(callback_query: types.CallbackQuery, state: FSMContext):
    chat_id = callback_query.data.split(';')[-1]
    await callback_query.message.edit_text('Введите номер машины')
    await state.set_state(Create_Task.add_num)
    await state.update_data(chat_id=chat_id)


@dp.callback_query_handler(lambda c: c.data.startswith('decline'), state="*")
async def process_callback_kb1btn1(callback_query: types.CallbackQuery, state: FSMContext):
    id = callback_query.data.split(';')[-1]
    text = callback_query.data.split(';')[-2]
    chat_id = callback_query.data.split(';')[-3]
    conn = sqlite3.connect('Data.db')
    cur = conn.cursor()
    cur.execute(f"SELECT service_name FROM autoservices WHERE chat_id={chat_id}")

    await bot.send_message(id, f'Заявка для машины {text} отклонена сервисом {str(cur.fetchone())[2:-3]}')
    await callback_query.message.edit_text(text="Спасибо",reply_markup=None)
    await state.finish()


@dp.callback_query_handler(lambda c: c.data.startswith('accept'), state="*")
async def process_callback_kb1btn1(callback_query: types.CallbackQuery, state: FSMContext):
    id = callback_query.data.split(';')[-1]
    text = callback_query.data.split(';')[-2]
    chat_id = callback_query.data.split(';')[-3]
    conn = sqlite3.connect('Data.db')
    cur = conn.cursor()
    cur.execute(f"SELECT service_name FROM autoservices WHERE chat_id={chat_id}")

    await bot.send_message(id, f'Заявка для машины {text} принята сервисом {str(cur.fetchone())[2:-3]}')
    await callback_query.message.edit_text(text="Спасибо",reply_markup=None)
    await state.finish()


@dp.message_handler(state=Create_Task.add_num)
async def read_num_of_car(message: types.Message, state: FSMContext):
    chat_id = await state.get_data()
    keyboard = InlineKeyboardMarkup().row(InlineKeyboardButton(text='accept', callback_data=f'accept;{chat_id["chat_id"]};{message.text};{message.chat.id}'), InlineKeyboardButton(text='decline', callback_data=f'decline;{chat_id["chat_id"]};{message.text};{message.chat.id}'))
    await bot.send_message(chat_id["chat_id"], text=f"Заявка на ремонт машины {message.text}", reply_markup=keyboard)
    await state.set_state(Create_Task.accepting)


@dp.message_handler(text=['мои заявки', 'Мои заявки', 'заявки', 'заявка'], state='*')
async def my_requests(message: types.Message):
    keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton('1', url='https://github.com/clovn/tg_bot')).add(InlineKeyboardButton('1', url='https://github.com/clovn/tg_bot'))
    await message.answer('Ваши заявки', reply_markup=keyboard)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)