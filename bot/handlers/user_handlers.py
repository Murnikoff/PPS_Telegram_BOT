from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from utils.db import add_task

router = Router()

class TaskStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()

@router.message(Command("create_task"))
async def create_task(message: Message, state: FSMContext):
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