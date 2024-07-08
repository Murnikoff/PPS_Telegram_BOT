from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from utils.db import add_task, get_active_task, complete_task

command_router = Router()

class TaskStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_comment = State()
    waiting_for_start_date = State()
    waiting_for_end_date = State()

@command_router.message(Command("create_task"))
async def create_task(message: Message, state: FSMContext):
    user_id = message.from_user.id
    active_task = get_active_task(user_id)
    if active_task:
        await message.answer(
            f"У вас уже есть активное дело: '{active_task[1]}'\n\n"
            f"Описание задачи: '{active_task[2]}'"
            )
    else:
        await message.answer("Введите название дела:")
        await state.set_state(TaskStates.waiting_for_title)

@command_router.message(TaskStates.waiting_for_title)
async def get_task_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Введите описание задачи:")
    await state.set_state(TaskStates.waiting_for_description)

@command_router.message(TaskStates.waiting_for_description)
async def get_task_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Введите комментарий к делу:")
    await state.set_state(TaskStates.waiting_for_comment)

@command_router.message(TaskStates.waiting_for_comment)
async def get_task_comment(message: Message, state: FSMContext):
    await state.update_data(comment=message.text)
    await message.answer("Введите дату начала задачи (в формате YYYY-MM-DD):")
    await state.set_state(TaskStates.waiting_for_start_date)

@command_router.message(TaskStates.waiting_for_start_date)
async def get_start_date(message: Message, state: FSMContext):
    await state.update_data(start_date=message.text)
    await message.answer("Введите дату завершения задачи (в формате YYYY-MM-DD):")
    await state.set_state(TaskStates.waiting_for_end_date)

@command_router.message(TaskStates.waiting_for_end_date)
async def get_end_date(message: Message, state: FSMContext):
    user_data = await state.get_data()
    title = user_data['title']
    description = user_data['description']
    comment = user_data['comment']
    start_date = user_data['start_date']
    end_date = message.text
    user_id = message.from_user.id
    add_task(user_id, title, description, comment, start_date, end_date)
    await message.answer(
            f"Ваше активное дело: '{title}'\n\n"
            f"Описание задачи: '{description}'\n\n"
            f"Комментарий: '{comment}'\n\n"
            f"Дата начала: {start_date}\n"
            f"Дата завершения: {end_date}\n\n"
            f"Успешно создано!"
        )
    await state.clear()

@command_router.message(Command("view_task"))
async def view_task(message: Message):
    user_id = message.from_user.id
    task = get_active_task(user_id)
    if task:
        await message.answer(
            f"Ваше активное дело: '{task[1]}'\n\n"
            f"Описание задачи: '{task[2]}'\n\n"
            f"Комментарий: '{task[3]}'\n\n"
            f"Дата начала: {task[4]}\n"
            f"Дата завершения: {task[5]}"
        )
    else:
        await message.answer("У вас нет активных дел.")

@command_router.message(Command("complete_active_task"))
async def complete_active_task(message: Message):
    user_id = message.from_user.id
    task = get_active_task(user_id)
    if task:
        complete_task(task[0])
        await message.answer(
            f"Ваше активное дело: '{task[1]}'\n\n"
            f"Описание задачи: '{task[2]}'\n\n"
            f"Успешно завершено!"
            )
    else:
        await message.answer("У вас нет активных дел.")

@command_router.message(Command("help"))
async def help_command(message: Message):
    help_text = (
        "/start - Начать работу с ботом\n"
        "/help - Показать это сообщение\n"
        "/create_task - Создать новое дело\n"
        "/view_task - Просмотреть активное дело\n"
        "/complete_active_task - Завершить активное дело\n"
    )
    await message.answer(help_text)

@command_router.message(Command("start"))
async def start_command(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Создать дело", callback_data="create_task")],
        [InlineKeyboardButton(text="Просмотреть дело", callback_data="view_task")],
        [InlineKeyboardButton(text="Завершить дело", callback_data="complete_task")],
        [InlineKeyboardButton(text="Помощь", callback_data="help")]
    ])
    await message.answer("Привет! Я бот для управления делами. Используйте кнопки ниже или команды для взаимодействия.", reply_markup=keyboard)