from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from utils.db import add_task, get_active_task

router = Router()

class TaskStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()

@router.message(Command("create_task"))
async def create_task(message: Message, state: FSMContext):
    user_id = message.from_user.id
    active_task = get_active_task(user_id)
    if active_task:
        await message.answer(f"У вас уже есть активное дело: '{active_task[1]}' - '{active_task[2]}'")
    else:
        await message.answer("Введите название дела:")
        await state.set_state(TaskStates.waiting_for_title)

@router.message(TaskStates.waiting_for_title)
async def get_task_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Введите описание задачи:")
    await state.set_state(TaskStates.waiting_for_description)

@router.message(TaskStates.waiting_for_description)
async def get_task_description(message: Message, state: FSMContext):
    user_data = await state.get_data()
    title = user_data['title']
    description = message.text
    user_id = message.from_user.id
    add_task(user_id, title, description)
    await message.answer(f"Дело '{title}' с описанием '{description}' создано и сохранено в базе данных!")
    await state.clear()

@router.message(Command("view_task"))
async def view_task(message: Message):
    user_id = message.from_user.id
    task = get_active_task(user_id)
    if task:
        await message.answer(f"Ваше активное дело: '{task[1]}' - '{task[2]}'")
    else:
        await message.answer("У вас нет активных дел.")

@router.message(Command("help"))
async def help_command(message: Message):
    help_text = (
        "/start - Начать работу с ботом\n"
        "/help - Показать это сообщение\n"
        "/create_task - Создать новое дело\n"
        "/view_task - Просмотреть активное дело\n"
    )
    await message.answer(help_text)

@router.message(Command("start"))
async def start_command(message: Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/create_task")],
            [KeyboardButton(text="/view_task")],
            [KeyboardButton(text="/help")]
        ],
        resize_keyboard=True
    )
    await message.answer("Привет! Я бот для управления делами. Используйте кнопки ниже или команды для взаимодействия.", reply_markup=keyboard)