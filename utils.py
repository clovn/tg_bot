from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


class Create_Task(StatesGroup):
    default = State()
    create = State()
    add_num = State()
    accepting = State()