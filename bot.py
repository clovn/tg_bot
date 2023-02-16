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
    conn = sqlite3.connect('Data.db')
    cur = conn.cursor()
    cur.execute("SELECT id FROM users")
    acessed_users = [i[0] for i in cur.fetchall()]
    if message.from_user.id in acessed_users:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(KeyboardButton('Создать заявку'))
        await message.answer("HI", reply_markup=keyboard)
        await state.set_state(Create_Task.default)


@dp.message_handler(text=['Создать заявку'], state=Create_Task.default)
async def send_welcome(message: types.Message, state: FSMContext):
    keyboard = InlineKeyboardMarkup(row_width=3)
    conn = sqlite3.connect('Data.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM autoservices")
    services = [list(i) for i in cur.fetchall()]
    conn.close()
    for i in services:
        keyboard.add(InlineKeyboardButton(text=i[1], callback_data=f"service_button;{i[0]}"))
    keyboard.add(InlineKeyboardButton(text='Cancel', callback_data="cancel_service"))
    await message.answer("Выберите сервис", reply_markup=keyboard)
    await state.set_state(Create_Task.create)


@dp.message_handler(state=Create_Task.create)
async def read_num_of_car(message: types.Message, state: FSMContext):
    chat_id = await state.get_data()
    keyboard = InlineKeyboardMarkup().row(InlineKeyboardButton(text='accept', callback_data=f'accept;{chat_id["chat_id"]};{message.text};{message.chat.id}'), InlineKeyboardButton(text='decline', callback_data=f'decline;{chat_id["chat_id"]};{message.text};{message.chat.id}'))
    await bot.send_message(chat_id["chat_id"], text=f"Заявка на ремонт машины {message.text}", reply_markup=keyboard)
    await state.set_state(Create_Task.accepting)


@dp.message_handler(text=['мои заявки', 'Мои заявки', 'заявки', 'заявка'], state='*')
async def my_requests(message: types.Message):
    keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton('1', url='https://github.com/clovn/tg_bot')).add(InlineKeyboardButton('1', url='https://github.com/clovn/tg_bot'))
    await message.answer('Ваши заявки', reply_markup=keyboard)


#CALLBACKS
@dp.callback_query_handler(lambda c: c.data.startswith('decline'), state="*")
async def process_callback_kb1btn1(callback_query: types.CallbackQuery, state: FSMContext):
    id = callback_query.data.split(';')[-1]
    text = callback_query.data.split(';')[-2]
    chat_id = callback_query.data.split(';')[-3]
    conn = sqlite3.connect('Data.db')
    cur = conn.cursor()
    conn.close()
    cur.execute(f"SELECT service_name FROM autoservices WHERE chat_id={chat_id}")

    await bot.send_message(id, f'Заявка для машины {text} отклонена сервисом {str(cur.fetchone())[2:-3]}')
    await callback_query.message.edit_text(text="Спасибо",reply_markup=None)
    await state.finish()


@dp.callback_query_handler(lambda c: c.data.startswith('cancel_service'), state="*")
async def process_callback_kb1btn1(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text('Заявка отменена')
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
    await callback_query.message.edit_text(text="Спасибо", reply_markup=None)
    await state.finish()
    conn.close()


@dp.callback_query_handler(lambda c: c.data.startswith('service_button'), state=Create_Task.create)
async def process_callback_kb1btn1(callback_query: types.CallbackQuery, state: FSMContext):
    chat_id = callback_query.data.split(';')[-1]
    webApp = types.WebAppInfo(url="https://clovn.github.io/")
    await callback_query.message.edit_text('Заполните форму', reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(text='Форма', web_app=webApp)).add(InlineKeyboardButton(text="Cancel", callback_data="cancel_service")))
    await state.update_data(chat_id=chat_id)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)