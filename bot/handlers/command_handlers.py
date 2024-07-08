from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from utils.db import add_task, get_active_task, complete_task, update_task

command_router = Router()

class TaskStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_comment = State()
    waiting_for_start_date = State()
    waiting_for_end_date = State()
    waiting_for_edit_field = State()
    waiting_for_edit_value = State()

@command_router.message(Command("create_task"))
async def create_task(message: Message, state: FSMContext):
    user_id = message.from_user.id
    active_task = get_active_task(user_id)
    if active_task:
        await message.answer(f"У вас уже есть активное дело: '{active_task[1]}'\n\nОписание задачи: '{active_task[2]}'")
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
    await message.answer(f"Дело: '{title}'\n\nОписание задачи: '{description}'\n\nКомментарий: '{comment}'\n\nДата начала: {start_date}\nДата завершения: {end_date}\n\nУспешно создано и сохранено!")
    await state.clear()

@command_router.message(Command("view_task"))
async def view_task(message: Message):
    user_id = message.from_user.id
    task = get_active_task(user_id)
    if task:
        await message.answer(f"Ваше активное дело: '{task[1]}'\n\nОписание задачи: '{task[2]}'\n\nКомментарий: '{task[3]}'\n\nДата начала: {task[4]}\nДата завершения: {task[5]}")
    else:
        await message.answer("У вас нет активных дел.")

@command_router.message(Command("complete_active_task"))
async def complete_active_task(message: Message):
    user_id = message.from_user.id
    task = get_active_task(user_id)
    if task:
        complete_task(task[0])
        await message.answer(f"Ваше активное дело: '{task[1]}'\n\nЗадача: '{task[2]}'\n\nУспешно завершено!")
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
        "/edit_task - Редактировать активное дело\n"
    )
    await message.answer(help_text)

@command_router.message(Command("edit_task"))
async def edit_task(message: Message, state: FSMContext):
    user_id = message.from_user.id
    task = get_active_task(user_id)
    if task:
        await message.answer("Какое поле вы хотите изменить? (title, description, comment, start_date, end_date)")
        await state.set_state(TaskStates.waiting_for_edit_field)
    else:
        await message.answer("У вас нет активных дел.")

@command_router.message(TaskStates.waiting_for_edit_field)
async def get_edit_field(message: Message, state: FSMContext):
    field = message.text
    if field not in ["title", "description", "comment", "start_date", "end_date"]:
        await message.answer("Неверное поле. Пожалуйста, введите одно из следующих: title, description, comment, start_date, end_date")
        return
    await state.update_data(edit_field=field)
    await message.answer(f"Введите новое значение для поля {field}:")
    await state.set_state(TaskStates.waiting_for_edit_value)

@command_router.message(TaskStates.waiting_for_edit_value)
async def get_edit_value(message: Message, state: FSMContext):
    user_data = await state.get_data()
    field = user_data['edit_field']
    value = message.text
    user_id = message.from_user.id
    task = get_active_task(user_id)
    if task:
        update_task(task[0], **{field: value})
        await message.answer(f"Поле {field} успешно обновлено!")
    else:
        await message.answer("У вас нет активных дел.")
    await state.clear()

@command_router.message(Command("start"))
async def start_command(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Создать дело", callback_data="create_task")],
        [InlineKeyboardButton(text="Просмотреть активное дело", callback_data="view_task")],
        [InlineKeyboardButton(text="Завершить активное дело", callback_data="complete_task")],
        [InlineKeyboardButton(text="Редактировать активное дело", callback_data="edit_task")],
        [InlineKeyboardButton(text="Помощь", callback_data="help")]
    ])
    await message.answer("Привет! Я бот для управления делами. Используйте кнопки ниже или команды для взаимодействия.", reply_markup=keyboard)