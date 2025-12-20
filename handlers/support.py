from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import keyboards as kb
from database import SessionLocal, SupportTicket, User
from datetime import datetime
import random

router = Router()

class SupportStates(StatesGroup):
    waiting_message = State()

@router.callback_query(F.data == "leave_review")
async def leave_review(callback: CallbackQuery):
    await callback.message.edit_text(
        "📝 *Оставить отзыв*\n\n"
        "Чтобы оставить отзыв, напишите нам в личные сообщения:\n"
        "@VenmoSell_Manager\n\n"
        "Лучшие отзывы публикуются в нашем канале!",
        parse_mode="Markdown",
        reply_markup=kb.back_button()
    )

# Обработка связи с менеджером уже реализована через кнопку с URL