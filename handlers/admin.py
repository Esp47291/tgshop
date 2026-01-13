from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import keyboards as kb
from database import SessionLocal, User, Order, Payment, SupportTicket, Referral
import config
from datetime import datetime, timedelta
import os
import logging

router = Router()
logger = logging.getLogger(__name__)


class AdminStates(StatesGroup):
    waiting_order_id = State()
    waiting_user_id = State()
    waiting_broadcast = State()


def is_admin(user_id: int) -> bool:
    """Проверка прав администратора"""
    # Преобразуем user_id в int на случай, если приходит строка
    user_id = int(user_id)
    # Преобразуем все ADMIN_IDS в int для сравнения
    admin_ids = [int(admin_id) for admin_id in config.ADMIN_IDS]
    result = user_id in admin_ids
    logger.debug(f"Admin check: user_id={user_id}, admin_ids={admin_ids}, result={result}")
    return result


@router.message(Command("admin"))
async def admin_panel(message: Message):
    user_id = message.from_user.id
    logger.info(f"Admin panel access attempt by user_id: {user_id} (type: {type(user_id).__name__})")
    logger.info(f"ADMIN_IDS from config: {config.ADMIN_IDS}")
    
    if not is_admin(user_id):
        logger.warning(f"Access denied for user_id: {user_id}. ADMIN_IDS: {config.ADMIN_IDS}")
        await message.answer("⛔ Доступ запрещен!")
        return
    
    logger.info(f"Access granted for user_id: {user_id}")

    with SessionLocal() as session:
        users_count = session.query(User).count()
        orders_count = session.query(Order).count()
        active_orders = session.query(Order).filter(Order.status == 'pending').count()
        paid_orders = session.query(Order).filter(Order.status == 'paid').count()
        
        total_revenue = sum([
            order.amount for order in session.query(Order).filter(Order.status == 'completed').all()
        ] or [0])

        stats_text = f"""
⚙️ *Админ-панель*

📊 *Статистика:*
• Пользователей: {users_count}
• Всего заказов: {orders_count}
• Ожидают оплаты: {active_orders}
• Оплачено (ожидают выдачи): {paid_orders}
• Доход: {total_revenue:.2f}$

Выберите действие:
"""

        await message.answer(
            stats_text,
            reply_markup=kb.admin_menu(),
            parse_mode="Markdown"
        )


@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Доступ запрещен!", show_alert=True)
        return

    with SessionLocal() as session:
        today = datetime.utcnow().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        # Пользователи
        users_total = session.query(User).count()
        users_today = session.query(User).filter(
            User.created_at >= datetime.combine(today, datetime.min.time())
        ).count()
        users_week = session.query(User).filter(User.created_at >= week_ago).count()
        users_month = session.query(User).filter(User.created_at >= month_ago).count()

        # Заказы
        orders_total = session.query(Order).count()
        orders_pending = session.query(Order).filter(Order.status == 'pending').count()
        orders_paid = session.query(Order).filter(Order.status == 'paid').count()
        orders_completed = session.query(Order).filter(Order.status == 'completed').count()
        orders_cancelled = session.query(Order).filter(Order.status == 'cancelled').count()

        # Финансы
        revenue_total = sum([
            order.amount for order in session.query(Order).filter(Order.status == 'completed').all()
        ] or [0])
        revenue_today = sum([
            order.amount for order in session.query(Order).filter(
                Order.status == 'completed',
                Order.completed_at >= datetime.combine(today, datetime.min.time())
            ).all()
        ] or [0])
        revenue_week = sum([
            order.amount for order in session.query(Order).filter(
                Order.status == 'completed',
                Order.completed_at >= week_ago
            ).all()
        ] or [0])
        revenue_month = sum([
            order.amount for order in session.query(Order).filter(
                Order.status == 'completed',
                Order.completed_at >= month_ago
            ).all()
        ] or [0])

        avg_order = revenue_total / orders_completed if orders_completed > 0 else 0

        # Рефералы
        active_referrers = session.query(User).filter(User.referrer_id.isnot(None)).count()
        total_referrals = session.query(Referral).count()
        referral_earnings = sum([
            ref.earned_amount for ref in session.query(Referral).all()
        ] or [0])

        # Тикеты
        tickets_open = session.query(SupportTicket).filter(SupportTicket.status == 'open').count()
        tickets_total = session.query(SupportTicket).count()

        stats_text = f"""
📊 *Подробная статистика*

👥 *Пользователи:*
• Всего: {users_total}
• Сегодня: {users_today}
• За неделю: {users_week}
• За месяц: {users_month}

📦 *Заказы:*
• Всего: {orders_total}
• Ожидают оплаты: {orders_pending}
• Оплачено (ожидают выдачи): {orders_paid}
• Выполнено: {orders_completed}
• Отменено: {orders_cancelled}

💰 *Финансы:*
• Общий доход: {revenue_total:.2f}$
• Сегодня: {revenue_today:.2f}$
• За неделю: {revenue_week:.2f}$
• За месяц: {revenue_month:.2f}$
• Средний чек: {avg_order:.2f}$

👥 *Рефералы:*
• Активных рефереров: {active_referrers}
• Всего рефералов: {total_referrals}
• Заработано рефералами: {referral_earnings:.2f}$

🎫 *Тикеты:*
• Открытых: {tickets_open}
• Всего: {tickets_total}
"""

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📥 Экспорт статистики", callback_data="admin_export_stats")],
            [InlineKeyboardButton(text="« Назад", callback_data="back_to_admin")]
        ])

        await callback.message.edit_text(
            stats_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )


@router.callback_query(F.data == "admin_export_stats")
async def export_stats(callback: CallbackQuery, bot: Bot):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Доступ запрещен!", show_alert=True)
        return

    try:
        with SessionLocal() as session:
            # Создание файла статистики
            stats_file = "data/stats_export.txt"
            
            with open(stats_file, "w", encoding="utf-8") as f:
                f.write("=" * 60 + "\n")
                f.write("ЭКСПОРТ СТАТИСТИКИ БОТА\n")
                f.write(f"Дата экспорта: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")

                # Пользователи
                users = session.query(User).all()
                f.write(f"ПОЛЬЗОВАТЕЛИ (Всего: {len(users)})\n")
                f.write("-" * 60 + "\n")
                for user in users:
                    f.write(f"ID: {user.id} | Telegram ID: {user.telegram_id} | "
                           f"Username: @{user.username or 'нет'} | "
                           f"Имя: {user.full_name or 'не указано'} | "
                           f"Баланс: {user.balance}$ | "
                           f"Потрачено: {user.total_spent}$ | "
                           f"Регистрация: {user.created_at}\n")
                f.write("\n")

                # Заказы
                orders = session.query(Order).all()
                f.write(f"ЗАКАЗЫ (Всего: {len(orders)})\n")
                f.write("-" * 60 + "\n")
                for order in orders:
                    f.write(f"ID: {order.id} | Order ID: {order.order_id} | "
                           f"User ID: {order.user_id} | "
                           f"Товар: {order.product} | "
                           f"Количество: {order.quantity} | "
                           f"Сумма: {order.amount}$ | "
                           f"Статус: {order.status} | "
                           f"Способ оплаты: {order.payment_method or 'N/A'} | "
                           f"Создан: {order.created_at}\n")
                f.write("\n")

                # Платежи
                payments = session.query(Payment).all()
                f.write(f"ПЛАТЕЖИ (Всего: {len(payments)})\n")
                f.write("-" * 60 + "\n")
                for payment in payments:
                    f.write(f"ID: {payment.id} | Order ID: {payment.order_id} | "
                           f"Сумма: {payment.amount}$ | "
                           f"Валюта: {payment.currency} | "
                           f"Сеть: {payment.crypto_network or 'N/A'} | "
                           f"Статус: {payment.status} | "
                           f"Хэш: {payment.transaction_hash or 'N/A'} | "
                           f"Создан: {payment.created_at}\n")
                f.write("\n")

                # Рефералы
                referrals = session.query(Referral).all()
                f.write(f"РЕФЕРАЛЫ (Всего: {len(referrals)})\n")
                f.write("-" * 60 + "\n")
                for ref in referrals:
                    f.write(f"ID: {ref.id} | Реферер: {ref.referrer_id} | "
                           f"Реферал: {ref.referred_id} | "
                           f"Заработано: {ref.earned_amount}$ | "
                           f"Статус: {ref.status} | "
                           f"Создан: {ref.created_at}\n")
                f.write("\n")

                # Тикеты
                tickets = session.query(SupportTicket).all()
                f.write(f"ТИКЕТЫ ПОДДЕРЖКИ (Всего: {len(tickets)})\n")
                f.write("-" * 60 + "\n")
                for ticket in tickets:
                    f.write(f"ID: {ticket.id} | Номер: {ticket.ticket_number} | "
                           f"User ID: {ticket.user_id} | "
                           f"Тема: {ticket.subject} | "
                           f"Статус: {ticket.status} | "
                           f"Создан: {ticket.created_at}\n")
                    f.write(f"Сообщение: {ticket.message[:100]}...\n")
                f.write("\n")

                # Общая статистика
                f.write("=" * 60 + "\n")
                f.write("ОБЩАЯ СТАТИСТИКА\n")
                f.write("=" * 60 + "\n")
                f.write(f"Всего пользователей: {len(users)}\n")
                f.write(f"Всего заказов: {len(orders)}\n")
                f.write(f"Всего платежей: {len(payments)}\n")
                f.write(f"Всего рефералов: {len(referrals)}\n")
                f.write(f"Всего тикетов: {len(tickets)}\n")
                
                total_revenue = sum([o.amount for o in orders if o.status == 'completed'])
                f.write(f"Общий доход: {total_revenue:.2f}$\n")

            # Отправка файла
            file = FSInputFile(stats_file)
            await bot.send_document(
                callback.from_user.id,
                document=file,
                caption="📊 Экспорт статистики"
            )
            
            await callback.answer("✅ Статистика экспортирована!", show_alert=True)
            
    except Exception as e:
        logger.error(f"Error exporting stats: {e}")
        await callback.answer("❌ Ошибка при экспорте статистики", show_alert=True)


@router.callback_query(F.data == "admin_orders")
async def admin_orders(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Доступ запрещен!", show_alert=True)
        return

    with SessionLocal() as session:
        pending_orders = session.query(Order).filter(Order.status == 'pending').limit(10).all()
        paid_orders = session.query(Order).filter(Order.status == 'paid').limit(10).all()

        orders_text = "📦 *Управление заказами*\n\n"
        
        if pending_orders:
            orders_text += "*Ожидают оплаты:*\n"
            for order in pending_orders:
                user = session.query(User).filter(User.id == order.user_id).first()
                orders_text += f"• `{order.order_id}` - {order.amount}$ - @{user.username or 'N/A'}\n"
        else:
            orders_text += "*Ожидают оплаты: нет*\n"
        
        orders_text += "\n"
        
        if paid_orders:
            orders_text += "*Оплачено (ожидают выдачи):*\n"
            for order in paid_orders:
                user = session.query(User).filter(User.id == order.user_id).first()
                orders_text += f"• `{order.order_id}` - {order.amount}$ - @{user.username or 'N/A'}\n"
        else:
            orders_text += "*Оплачено: нет*\n"

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Подтвердить платеж", callback_data="admin_confirm_payment")],
            [InlineKeyboardButton(text="🎁 Выдать товар", callback_data="admin_deliver")],
            [InlineKeyboardButton(text="📋 Все заказы", callback_data="admin_all_orders")],
            [InlineKeyboardButton(text="« Назад", callback_data="back_to_admin")]
        ])

        await callback.message.edit_text(
            orders_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )


@router.callback_query(F.data == "admin_confirm_payment")
async def admin_confirm_payment_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Доступ запрещен!", show_alert=True)
        return

    await callback.message.edit_text(
        "💳 *Подтверждение платежа*\n\n"
        "Введите Order ID заказа для подтверждения платежа:",
        parse_mode="Markdown"
    )
    await state.set_state(AdminStates.waiting_order_id)


@router.message(AdminStates.waiting_order_id)
async def admin_confirm_payment_process(message: Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Доступ запрещен!")
        await state.clear()
        return

    data = await state.get_data()
    action = data.get("action", "confirm")
    order_id = message.text.strip()
    
    with SessionLocal() as session:
        order = session.query(Order).filter(Order.order_id == order_id).first()
        
        if not order:
            await message.answer(f"❌ Заказ `{order_id}` не найден", parse_mode="Markdown")
            await state.clear()
            return
        
        if action == "deliver":
            # Выдача товара
            if order.status != "paid":
                await message.answer(
                    f"⚠️ Заказ `{order_id}` не оплачен (статус: {order.status})",
                    parse_mode="Markdown"
                )
                await state.clear()
                return
            
            # Импорт функции доставки из payments.py
            from handlers.payments import deliver_product
            
            try:
                await deliver_product(bot, order, session)
                await message.answer(
                    f"✅ Товар по заказу `{order_id}` успешно выдан!",
                    parse_mode="Markdown"
                )
            except Exception as e:
                logger.error(f"Error delivering product: {e}")
                await message.answer(
                    f"❌ Ошибка при выдаче товара: {str(e)}",
                    parse_mode="Markdown"
                )
        else:
            # Подтверждение платежа
            if order.status == "completed":
                await message.answer(f"⚠️ Заказ `{order_id}` уже выполнен", parse_mode="Markdown")
                await state.clear()
                return
            
            order.status = "paid"
            session.commit()
            
            # Обновление платежа
            payment = session.query(Payment).filter(Payment.order_id == order.id).first()
            if payment:
                payment.status = "confirmed"
                payment.confirmed_at = datetime.utcnow()
                session.commit()
            
            # Уведомление пользователя
            user = session.query(User).filter(User.id == order.user_id).first()
            if user:
                await bot.send_message(
                    user.telegram_id,
                    f"✅ *Платеж подтвержден!*\n\n"
                    f"Заказ `{order.order_id}` оплачен.\n"
                    f"Товар будет выдан в ближайшее время.",
                    parse_mode="Markdown"
                )
            
            await message.answer(
                f"✅ Платеж по заказу `{order_id}` подтвержден!",
                parse_mode="Markdown"
            )
        
        await state.clear()


@router.callback_query(F.data == "admin_deliver")
async def admin_deliver_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Доступ запрещен!", show_alert=True)
        return

    await callback.message.edit_text(
        "🎁 *Выдача товара*\n\n"
        "Введите Order ID заказа для выдачи товара:",
        parse_mode="Markdown"
    )
    await state.update_data(action="deliver")
    await state.set_state(AdminStates.waiting_order_id)


@router.callback_query(F.data == "admin_all_orders")
async def admin_all_orders(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Доступ запрещен!", show_alert=True)
        return

    with SessionLocal() as session:
        orders = session.query(Order).order_by(Order.created_at.desc()).limit(20).all()
        
        orders_text = "📦 *Все заказы (последние 20)*\n\n"
        
        for order in orders:
            user = session.query(User).filter(User.id == order.user_id).first()
            status_emoji = {
                "pending": "⏳",
                "paid": "✅",
                "completed": "🎁",
                "cancelled": "❌"
            }.get(order.status, "❓")
            
            orders_text += f"{status_emoji} `{order.order_id}` - {order.amount}$ - "
            orders_text += f"@{user.username or 'N/A'} - {order.status}\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="« Назад", callback_data="admin_orders")]
        ])
        
        await callback.message.edit_text(
            orders_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )


@router.callback_query(F.data == "admin_users")
async def admin_users(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Доступ запрещен!", show_alert=True)
        return

    with SessionLocal() as session:
        users = session.query(User).order_by(User.created_at.desc()).limit(20).all()
        
        users_text = "👤 *Пользователи (последние 20)*\n\n"
        
        for user in users:
            orders_count = session.query(Order).filter(Order.user_id == user.id).count()
            users_text += f"@{user.username or 'нет'} ({user.telegram_id})\n"
            users_text += f"Баланс: {user.balance}$ | Потрачено: {user.total_spent}$ | "
            users_text += f"Заказов: {orders_count}\n\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="« Назад", callback_data="back_to_admin")]
        ])
        
        await callback.message.edit_text(
            users_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )


@router.callback_query(F.data == "admin_payments")
async def admin_payments(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Доступ запрещен!", show_alert=True)
        return

    with SessionLocal() as session:
        pending_payments = session.query(Payment).filter(Payment.status == 'pending').limit(10).all()
        
        payments_text = "💸 *Платежи, требующие проверки*\n\n"
        
        if pending_payments:
            for payment in pending_payments:
                order = session.query(Order).filter(Order.id == payment.order_id).first()
                user = session.query(User).filter(User.id == order.user_id).first() if order else None
                
                payments_text += f"💰 {payment.amount}$ - {payment.crypto_network or 'N/A'}\n"
                payments_text += f"Заказ: `{order.order_id if order else 'N/A'}` | "
                payments_text += f"Пользователь: @{user.username if user else 'N/A'}\n"
                if payment.transaction_hash:
                    payments_text += f"Хэш: `{payment.transaction_hash[:20]}...`\n"
                payments_text += "\n"
        else:
            payments_text += "Нет платежей, требующих проверки"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="« Назад", callback_data="back_to_admin")]
        ])
        
        await callback.message.edit_text(
            payments_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )


@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Доступ запрещен!", show_alert=True)
        return

    await callback.message.edit_text(
        "✉️ *Рассылка сообщений*\n\n"
        "Введите сообщение для рассылки всем пользователям:",
        parse_mode="Markdown"
    )
    await state.set_state(AdminStates.waiting_broadcast)


@router.message(AdminStates.waiting_broadcast)
async def admin_broadcast_send(message: Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Доступ запрещен!")
        await state.clear()
        return

    broadcast_text = message.text or (message.caption if message.caption else "")
    
    with SessionLocal() as session:
        users = session.query(User).all()
        sent = 0
        failed = 0
        
        for user in users:
            try:
                if message.photo:
                    await bot.send_photo(
                        user.telegram_id,
                        photo=message.photo[-1].file_id,
                        caption=broadcast_text
                    )
                else:
                    await bot.send_message(user.telegram_id, broadcast_text)
                sent += 1
            except Exception as e:
                logger.error(f"Error sending broadcast to {user.telegram_id}: {e}")
                failed += 1
        
        await message.answer(
            f"✅ Рассылка завершена!\n"
            f"Отправлено: {sent}\n"
            f"Ошибок: {failed}"
        )
        
        await state.clear()


@router.callback_query(F.data == "back_to_admin")
async def back_to_admin_menu(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Доступ запрещен!", show_alert=True)
        return

    with SessionLocal() as session:
        users_count = session.query(User).count()
        orders_count = session.query(Order).count()
        active_orders = session.query(Order).filter(Order.status == 'pending').count()
        paid_orders = session.query(Order).filter(Order.status == 'paid').count()
        
        total_revenue = sum([
            order.amount for order in session.query(Order).filter(Order.status == 'completed').all()
        ] or [0])

        stats_text = f"""
⚙️ *Админ-панель*

📊 *Статистика:*
• Пользователей: {users_count}
• Всего заказов: {orders_count}
• Ожидают оплаты: {active_orders}
• Оплачено (ожидают выдачи): {paid_orders}
• Доход: {total_revenue:.2f}$

Выберите действие:
"""

        await callback.message.edit_text(
            stats_text,
            reply_markup=kb.admin_menu(),
            parse_mode="Markdown"
        )
