from aiogram import Router
from aiogram.types import CallbackQuery
from utils.db import get_active_task, complete_task
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

callback_router = Router()

class TaskStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_comment = State()
    waiting_for_start_date = State()
    waiting_for_end_date = State()

@callback_router.callback_query(lambda c: c.data == 'create_task')
async def process_create_task_callback(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    active_task = get_active_task(user_id)
    if active_task:
        await callback_query.message.answer(f"У вас уже есть активное дело: '{active_task[1]}'\n\nЗадача: '{active_task[2]}'")
    else:
        await callback_query.message.answer("Введите название дела:")
        await state.set_state(TaskStates.waiting_for_title)
    await callback_query.answer()

@callback_router.callback_query(lambda c: c.data == 'view_task')
async def process_view_task_callback(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    task = get_active_task(user_id)
    if task:
        await callback_query.message.answer(
            f"Ваше активное дело: '{task[1]}'\n\n"
            f"Описание задачи: '{task[2]}'\n\n"
            f"Комментарий: '{task[3]}'\n\n"
            f"Дата начала: {task[4]}\n"
            f"Дата завершения: {task[5]}"
        )
    else:
        await callback_query.message.answer("У вас нет активных дел.")
    await callback_query.answer()

@callback_router.callback_query(lambda c: c.data == 'complete_task')
async def process_complete_task_callback(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    task = get_active_task(user_id)
    if task:
        complete_task(task[0])
        await callback_query.message.answer(
            f"Ваше активное дело: '{task[1]}'\n\n"
            f"Задача: '{task[2]}'\n\n"
            f"Успешно завершено!"
        )
    else:
        await callback_query.message.answer("У вас нет активных дел.")
    await callback_query.answer()

@callback_router.callback_query(lambda c: c.data == 'help')
async def process_help_callback(callback_query: CallbackQuery):
    help_text = (
        "/start - Начать работу с ботом\n"
        "/help - Показать это сообщение\n"
        "/create_task - Создать новое дело\n"
        "/view_task - Просмотреть активное дело\n"
        "/complete_active_task - Завершить активное дело\n"
    )
    await callback_query.message.answer(help_text)
    await callback_query.answer()