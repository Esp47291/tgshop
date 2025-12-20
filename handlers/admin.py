from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import keyboards as kb
from database import SessionLocal, User, Order, Payment
import config

router = Router()


@router.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id not in config.ADMIN_IDS:
        await message.answer("⛔ Доступ запрещен!")
        return

    with SessionLocal() as session:
        users_count = session.query(User).count()
        orders_count = session.query(Order).count()
        active_orders = session.query(Order).filter(Order.status == 'pending').count()

        stats_text = f"""
        ⚙️ *Админ-панель*

        Статистика:
        • Пользователей: {users_count}
        • Всего заказов: {orders_count}
        • Активных заказов: {active_orders}
        • Доход: {sum([order.amount for order in session.query(Order).filter(Order.status == 'completed').all()] or [0])}$

        Выберите действие:
        """

        await message.answer(
            stats_text,
            reply_markup=kb.admin_menu(),
            parse_mode="Markdown"
        )


@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    with SessionLocal() as session:
        # Подробная статистика
        stats = {
            "users": session.query(User).count(),
            "new_today": session.query(User).filter(
                User.created_at >= datetime.now().date()
            ).count(),
            "orders": session.query(Order).count(),
            "revenue": sum(
                [order.amount for order in session.query(Order).filter(Order.status == 'completed').all()] or [0])
        }

        stats_text = f"""
        📊 *Подробная статистика*

        👥 Пользователи:
        • Всего: {stats['users']}
        • Новых сегодня: {stats['new_today']}

        📦 Заказы:
        • Всего: {stats['orders']}
        • Ожидают оплаты: {session.query(Order).filter(Order.status == 'pending').count()}
        • Выполнено: {session.query(Order).filter(Order.status == 'completed').count()}

        💰 Финансы:
        • Общий доход: {stats['revenue']}$
        • Средний чек: {stats['revenue'] / stats['orders'] if stats['orders'] > 0 else 0}$

        👥 Рефералы:
        • Активных рефереров: {session.query(User).filter(User.referrer_id.isnot(None)).count()}
        """

        await callback.message.edit_text(
            stats_text,
            parse_mode="Markdown"
        )