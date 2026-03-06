from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import keyboards as kb
import config
from database import SessionLocal, SupportTicket, User
from datetime import datetime
import random
import logging

router = Router()
logger = logging.getLogger(__name__)


class SupportStates(StatesGroup):
    waiting_message = State()
    waiting_subject = State()


@router.callback_query(F.data == "leave_review")
async def leave_review(callback: CallbackQuery):
    await callback.message.edit_text(
        "📝 *Оставить отзыв*\n\n"
        "Чтобы оставить отзыв, напишите нам в личные сообщения:\n"
        f"@{config.SUPPORT_MANAGER_ID.replace('@', '')}\n\n"
        "Лучшие отзывы публикуются в нашем канале!",
        parse_mode="Markdown",
        reply_markup=kb.back_button()
    )


@router.callback_query(F.data == "create_ticket")
async def create_ticket_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📝 *Создание обращения в поддержку*\n\n"
        "Пожалуйста, укажите тему обращения:\n"
        "(Например: Проблема с оплатой, Вопрос о товаре и т.д.)",
        parse_mode="Markdown",
        reply_markup=kb.back_button()
    )
    await state.set_state(SupportStates.waiting_subject)


@router.message(SupportStates.waiting_subject)
async def process_subject(message: Message, state: FSMContext):
    subject = message.text.strip()
    if len(subject) < 5:
        await message.answer("❌ Тема слишком короткая. Пожалуйста, укажите более подробную тему.")
        return

    await state.update_data(subject=subject)
    await message.answer(
        "📝 Теперь опишите вашу проблему или вопрос подробно:\n\n"
        "⚠️ *Правила обращения:*\n"
        "• Будьте вежливы и точны\n"
        "• Опишите проблему четко\n"
        "• Не спамьте - одно подробное сообщение лучше 10 коротких\n"
        "• Укажите номер заказа, если есть",
        parse_mode="Markdown"
    )
    await state.set_state(SupportStates.waiting_message)


@router.message(SupportStates.waiting_message)
async def process_ticket_message(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    subject = data.get("subject", "Без темы")
    ticket_message = message.text or (message.caption if message.caption else "Сообщение без текста")

    with SessionLocal() as session:
        user = session.query(User).filter(User.telegram_id == message.from_user.id).first()
        if not user:
            await message.answer("❌ Ошибка: пользователь не найден. Используйте /start")
            await state.clear()
            return

        ticket_number = f"TKT{random.randint(100000, 999999)}"

        ticket = SupportTicket(
            ticket_number=ticket_number,
            user_id=user.id,
            subject=subject,
            message=ticket_message,
            status="open",
            created_at=datetime.utcnow()
        )
        session.add(ticket)
        session.commit()

        confirmation_text = f"""
✅ *Обращение создано!*

Номер обращения: `{ticket_number}`
Тема: {subject}

Ваше обращение передано менеджеру поддержки.
Ответ придет в течение 24 часов.

Менеджер поддержки: @{config.SUPPORT_MANAGER_ID.replace('@', '')}
"""

        await message.answer(
            confirmation_text,
            parse_mode="Markdown",
            reply_markup=kb.back_button()
        )

        manager_notification = f"""
🆕 *Новое обращение в поддержку*

Номер: `{ticket_number}`
Тема: {subject}

👤 Пользователь: @{message.from_user.username or 'без username'} ({message.from_user.id})
📝 Сообщение:
{ticket_message}

Ответить: /admin
"""

        try:
            manager_id = config.SUPPORT_MANAGER_ID
            if manager_id.startswith("@"):
                # Если username, можно отправить в личку или канал – здесь пример отправки в личку, если ID
                pass
            else:
                try:
                    manager_id_int = int(manager_id)
                    await bot.send_message(manager_id_int, manager_notification, parse_mode="Markdown")
                except ValueError:
                    pass
        except Exception as e:
            logger.error(f"Error sending notification to manager: {e}")

        for admin_id in config.ADMIN_IDS:
            try:
                if message.photo:
                    await bot.send_photo(
                        admin_id,
                        photo=message.photo[-1].file_id,
                        caption=manager_notification,
                        parse_mode="Markdown"
                    )
                else:
                    await bot.send_message(admin_id, manager_notification, parse_mode="Markdown")
            except Exception as e:
                logger.error(f"Error sending notification to admin {admin_id}: {e}")

        await state.clear()


@router.message(F.text)
async def support_keyword_handler(message: Message):
    keywords = ('поддержка', 'помощь', 'support', 'help')
    if any(keyword in message.text.lower() for keyword in keywords):
        support_text = """
🛠 *Техническая поддержка*

@{}

---
*Нужна помощь? Обращайся правильно!*

*Правила обращения:*
• Будь вежлив и точен – опиши проблему четко
• Не спрашивай о статусе чека – обработка до 15 минут
• Нет спаму! Одно подробное сообщение > 10 коротких

---
*Мы решим вопрос быстро, если ты следуешь правилам!*

**PS. Чем точнее опишешь проблему, тем быстрее получишь решение.**
""".format(config.SUPPORT_MANAGER_ID.replace('@', ''))

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📝 Создать обращение", callback_data="create_ticket")],
            [InlineKeyboardButton(text="📞 Связаться с менеджером",
                                  url=f"https://t.me/{config.SUPPORT_MANAGER_ID.replace('@', '')}")],
            [InlineKeyboardButton(text="📝 Оставить отзыв", callback_data="leave_review")],
            [InlineKeyboardButton(text="« Вернуться назад", callback_data="back_to_main")]
        ])

        await message.answer(
            support_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )