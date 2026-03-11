import os
from datetime import datetime
import random
import logging

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import keyboards as kb
import config
from database import SessionLocal, Order, Payment, User, Referral
from utils.payment_utils import get_cryptobot_api, CryptoPaymentChecker

router = Router()
logger = logging.getLogger(__name__)

payment_checker = CryptoPaymentChecker()


class PaymentStates(StatesGroup):
    waiting_screenshot = State()
    waiting_transaction_hash = State()


@router.callback_query(F.data == "payment_cryptobot")
async def cryptobot_payment(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    with SessionLocal() as session:
        user = session.query(User).filter(User.telegram_id == callback.from_user.id).first()
        if not user:
            await callback.answer("Ошибка: пользователь не найден", show_alert=True)
            return

        order = Order(
            order_id=f"ORD{random.randint(100000, 999999)}",
            user_id=user.id,
            product="Venmo Accounts",
            quantity=data.get("quantity", 1),
            amount=data.get("price", 10),
            status="pending",
            payment_method="CryptoBot",
            created_at=datetime.utcnow()
        )
        session.add(order)
        session.commit()

        await state.update_data(order_id=order.id, order_db_id=order.id)

        cryptobot = get_cryptobot_api()
        invoice = None

        if cryptobot:
            invoice = await cryptobot.create_invoice(
                amount=data.get("price", 10),
                description=f"Заказ {order.order_id} - Venmo Accounts x{data.get('quantity', 1)}",
                payload=str(order.id)
            )

        if invoice:
            invoice_url = invoice.get("pay_url", "")
            invoice_id = invoice.get("invoice_id")

            order.transaction_id = str(invoice_id)
            session.commit()

            payment_text = f"""
💳 *Оплата через CryptoBot*

*Шаг 2 из 3... Оплата товара*

ID заказа: `{order.order_id}`
Товар: Venmo Accounts
Количество: {data.get('quantity', 1)} шт
Сумма заказа: {data.get('price', 10)}$

Нажмите кнопку ниже для оплаты:
"""

            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="💳 Оплатить счет", url=invoice_url)],
                [InlineKeyboardButton(text="✅ Проверить оплату", callback_data=f"check_cryptobot:{invoice_id}")],
                [InlineKeyboardButton(text="« Назад", callback_data="back_to_payment")]
            ])

            await callback.message.edit_text(
                payment_text,
                reply_mup=keyboard,
                parse_mode="Markdown"
            )
        else:
            payment_text = f"""
💳 *Оплата через CryptoBot*

*Шаг 2 из 3... Оплата товара*

ID заказа: `{order.order_id}`
Товар: Venmo Accounts
Количество: {data.get('quantity', 1)} шт
Сумма заказа: {data.get('price', 10)}$

⚠️ CryptoBot временно недоступен. Пожалуйста, используйте оплату криптовалютой.
"""
            await callback.message.edit_text(
                payment_text,
                reply_markup=kb.payment_methods(),
                parse_mode="Markdown"
            )


@router.callback_query(F.data == "payment_crypto")
async def crypto_payment(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    with SessionLocal() as session:
        user = session.query(User).filter(User.telegram_id == callback.from_user.id).first()
        if not user:
            await callback.answer("Ошибка: пользователь не найден", show_alert=True)
            return

        order = Order(
            order_id=f"ORD{random.randint(100000, 999999)}",
            user_id=user.id,
            product="Venmo Accounts",
            quantity=data.get("quantity", 1),
            amount=data.get("price", 10),
            status="pending",
            payment_method="Crypto",
            created_at=datetime.utcnow()
        )
        session.add(order)
        session.commit()

        await state.update_data(order_id=order.id, order_db_id=order.id)

        payment_text = f"""
₿ *Оплата криптовалютой*

*Шаг 2 из 3... Оплата товара*

ID заказа: `{order.order_id}`
Товар: Venmo Accounts
Количество: {data.get('quantity', 1)} шт
Сумма к оплате: {data.get('price', 10)}$

Выберите сеть для оплаты:
"""

        await callback.message.edit_text(
            payment_text,
            reply_markup=kb.crypto_networks(),
            parse_mode="Markdown"
        )


@router.callback_query(F.data.startswith("network_"))
async def choose_network(callback: CallbackQuery, state: FSMContext):
    network = callback.data.split("_")[1]
    data = await state.get_data()

    networks_map = {
        "trc20": "USDT (TRC20)",
        "bep20": "USDT (BEP20)",
        "ton": "TON",
        "eth": "ETH"
    }

    wallet_info = payment_checker.get_wallet_info(network)
    wallet_address = wallet_info["address"]
    network_name = wallet_info["network"]

    if not wallet_address:
        await callback.answer("Ошибка: адрес кошелька не настроен", show_alert=True)
        return

    with SessionLocal() as session:
        order = session.query(Order).filter(Order.id == data.get("order_db_id")).first()
        if order:
            payment = Payment(
                order_id=order.id,
                amount=order.amount,
                currency="USD",
                crypto_network=network,
                wallet_address=wallet_address,
                status="pending",
                created_at=datetime.utcnow()
            )
            session.add(payment)
            session.commit()
            await state.update_data(payment_id=payment.id)

    payment_text = f"""
💰 *Оплата через {network_name}*

*Инструкция по оплате:*

1️⃣ Отправьте *{data.get('price', 10)}$* на адрес:

    2️⃣ После отправки:
       • Отправьте скриншот транзакции (фото)
       • ИЛИ отправьте хэш транзакции (текст)

    3️⃣ Платеж будет проверен в течение 5-15 минут

    *Внимание:* 
    • Отправляйте точную сумму!
    • Проверьте адрес перед отправкой
    • Сохраните хэш транзакции

    ID заказа: `{data.get('order_id', 'N/A')}`
    """

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Скопировать адрес", callback_data=f"copy_wallet:{wallet_address}")],
        [InlineKeyboardButton(text="« Назад", callback_data="back_to_payment")]
    ])

    await callback.message.edit_text(
        payment_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

    await state.set_state(PaymentStates.waiting_screenshot)
    await state.update_data(wallet_network=network, wallet_address=wallet_address)


@router.message(PaymentStates.waiting_screenshot)
async def receive_payment_proof(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()

    with SessionLocal() as session:
        order = session.query(Order).filter(Order.id == data.get("order_db_id")).first()
        if not order:
            await message.answer("❌ Ошибка: заказ не найден")
            await state.clear()
            return

        payment = session.query(Payment).filter(Payment.id == data.get("payment_id")).first()
        if not payment:
            await message.answer("❌ Ошибка: платеж не найден")
            await state.clear()
            return

        if message.photo:
            photo_file_id = message.photo[-1].file_id
            # Генерируем уникальное имя файла
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"order_{order.order_id}_{timestamp}.jpg"
            file_path = f"data/screenshots/{filename}"
            try:
                photo_file = await bot.get_file(photo_file_id)
                await photo_file.download(file_path)
                payment.screenshot_path = file_path
                logger.info(f"Screenshot saved: {file_path}")
            except Exception as e:
                logger.error(f"Error downloading screenshot: {e}")
                # Уведомляем пользователя, но не прерываем процесс
                await message.answer(
                    "⚠️ Не удалось сохранить скриншот, но ваш платеж принят. Администратор проверит вручную.")

        elif message.text:
            payment.transaction_hash = message.text.strip()

        payment.status = "pending"
        session.commit()

        user = session.query(User).filter(User.id == order.user_id).first()

        await message.answer(
            "✅ Доказательство оплаты получено!\n\n"
            "Платеж проверяется администратором.\n"
            "Статус обновится в течение 5-15 минут.\n\n"
            f"ID заказа: `{order.order_id}`",
            reply_markup=kb.back_button(),
            parse_mode="Markdown"
        )

        # Уведомление админа
        admin_notification = f"""
    🆕 *Новый платеж требует проверки!*

    👤 Пользователь: @{message.from_user.username or 'без username'} ({message.from_user.id})
    📦 Заказ: `{order.order_id}`
    💰 Сумма: {order.amount}$
    🌐 Сеть: {payment.crypto_network or 'N/A'}
    📍 Кошелек: `{payment.wallet_address[:20]}...`
    """

        if payment.transaction_hash:
            admin_notification += f"\n🔗 Хэш: `{payment.transaction_hash}`"

        admin_notification += f"\n\nПроверить: /admin"

        for admin_id in config.ADMIN_IDS:
            try:
                if message.photo:
                    await bot.send_photo(
                        admin_id,
                        photo=message.photo[-1].file_id,
                        caption=admin_notification,
                        parse_mode="Markdown"
                    )
                else:
                    await bot.send_message(admin_id, admin_notification, parse_mode="Markdown")
            except Exception as e:
                logger.error(f"Error sending notification to admin {admin_id}: {e}")

        await state.clear()


@router.callback_query(F.data.startswith("check_cryptobot:"))
async def check_cryptobot_payment(callback: CallbackQuery, state: FSMContext):
    invoice_id = int(callback.data.split(":")[1])
    data = await state.get_data()

    cryptobot = get_cryptobot_api()
    if not cryptobot:
        await callback.answer("CryptoBot API недоступен", show_alert=True)
        return

    invoice = await cryptobot.get_invoice_status(invoice_id)

    if invoice and invoice.get("status") == "paid":
        with SessionLocal() as session:
            order = session.query(Order).filter(Order.id == data.get("order_db_id")).first()
            if order and order.status == "pending":
                order.status = "paid"
                session.commit()

                payment = Payment(
                    order_id=order.id,
                    amount=order.amount,
                    currency="USD",
                    transaction_id=str(invoice_id),
                    status="confirmed",
                    confirmed_at=datetime.utcnow()
                )
                session.add(payment)
                session.commit()

                await deliver_product(callback.bot, order, session)

        await callback.answer("✅ Платеж подтвержден! Товар выдан.", show_alert=True)
        await callback.message.edit_text(
            "✅ *Платеж подтвержден!*\n\nТовар отправлен вам в личные сообщения.",
            parse_mode="Markdown"
        )
    else:
        await callback.answer("⏳ Платеж еще не подтвержден", show_alert=True)


@router.callback_query(F.data.startswith("copy_wallet:"))
async def copy_wallet_address(callback: CallbackQuery):
    wallet_address = callback.data.split(":")[1]
    await callback.answer(f"Адрес скопирован: {wallet_address[:10]}...", show_alert=True)


@router.callback_query(F.data == "back_to_payment")
async def back_to_payment_methods(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    payment_text = f"""
    🛒 *Подтверждение заказа*

    Товар: Venmo Accounts
    Количество: {data.get('quantity', 1)} шт
    Сумма: {data.get('price', 105)}$

    Все верно? Выберите способ оплаты:
    """

    await callback.message.edit_text(
        payment_text,
        reply_markup=kb.payment_methods(),
        parse_mode="Markdown"
    )


async def deliver_product(bot: Bot, order: Order, session):
    try:
        user = session.query(User).filter(User.id == order.user_id).first()
        if not user:
            return

        product_data = []
        for i in range(order.quantity):
            account_data = {
                "email": f"venmo{order.id}_{i + 1}@example.com",
                "password": f"Pass{order.id}_{i + 1}!",
                "username": f"venmo_user_{order.id}_{i + 1}"
            }
            product_data.append(account_data)

        delivery_text = f"""
    ✅ *Ваш заказ выполнен!*

    ID заказа: `{order.order_id}`
    Товар: Venmo Accounts
    Количество: {order.quantity} шт

    *Данные аккаунтов:*
    """

        for idx, account in enumerate(product_data, 1):
            delivery_text += f"""
    *Аккаунт {idx}:*
    Email: `{account['email']}`
    Password: `{account['password']}`
    Username: `{account['username']}`
    """

        delivery_text += "\n⚠️ Сохраните эти данные в безопасном месте!"

        await bot.send_message(
            user.telegram_id,
            delivery_text,
            parse_mode="Markdown"
        )

        order.status = "completed"
        order.completed_at = datetime.utcnow()
        user.total_spent += order.amount

        if user.referrer_id:
            referrer = session.query(User).filter(User.id == user.referrer_id).first()
            if referrer:
                referral_bonus = order.amount * (config.REFERRAL_PERCENT / 100)
                referrer.balance += referral_bonus

                referral = Referral(
                    referrer_id=referrer.id,
                    referred_id=user.id,
                    earned_amount=referral_bonus,
                    status="active"
                )
                session.add(referral)

        session.commit()

        logger.info(f"Product delivered for order {order.order_id}")

    except Exception as e:
        logger.error(f"Error delivering product: {e}")