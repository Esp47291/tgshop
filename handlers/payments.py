from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, PreCheckoutQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import keyboards as kb
import config
from database import SessionLocal, Order, Payment, User
from datetime import datetime
import random
import aiohttp

router = Router()


class PaymentStates(StatesGroup):
    waiting_screenshot = State()


@router.callback_query(F.data == "payment_cryptobot")
async def cryptobot_payment(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    # Создание заказа в базе
    with SessionLocal() as session:
        user = session.query(User).filter(User.telegram_id == callback.from_user.id).first()

        order = Order(
            order_id=f"ORD{random.randint(100000, 999999)}",
            user_id=user.id,
            product="Venmo Accounts",
            quantity=data.get("quantity", 1),
            amount=data.get("price", 105),
            status="pending",
            created_at=datetime.utcnow()
        )
        session.add(order)
        session.commit()

        await state.update_data(order_id=order.id)

        # Здесь должна быть интеграция с CryptoBot API
        # Для примера создаем заглушку
        payment_text = f"""
        💳 *Оплата через CryptoBot*

        *Шаг 2 из 3... Оплата товара*

        ID заказа: {order.order_id}
        Товар: Venmo Accounts
        Количество: {data.get('quantity', 1)} шт
        Сумма заказа: {data.get('price', 105)}$

        Для оплаты нажмите кнопку ниже:
        """

        await callback.message.edit_text(
            payment_text,
            reply_markup=kb.cryptobot_payment(),
            parse_mode="Markdown"
        )


@router.callback_query(F.data == "payment_crypto")
async def crypto_payment(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    with SessionLocal() as session:
        user = session.query(User).filter(User.telegram_id == callback.from_user.id).first()

        order = Order(
            order_id=f"ORD{random.randint(100000, 999999)}",
            user_id=user.id,
            product="Venmo Accounts",
            quantity=data.get("quantity", 1),
            amount=data.get("price", 105),
            status="pending",
            created_at=datetime.utcnow()
        )
        session.add(order)
        session.commit()

        await state.update_data(order_id=order.id)

        payment_text = f"""
        ₿ *Оплата криптовалютой*

        *Шаг 2 из 3... Оплата товара*

        ID заказа: {order.order_id}
        Товар: Venmo Accounts
        Количество: {data.get('quantity', 1)} шт
        Сумма к оплате: {data.get('price', 105)}$

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

    wallet_key = f"USDT_{network.upper()}" if network in ["trc20", "bep20"] else network.upper()
    wallet_address = config.WALLETS.get(wallet_key, "")

    payment_text = f"""
    💰 *Оплата через {networks_map[network]}*

    *Инструкция по оплате:*

    1. Отправьте {data.get('price', 105)}$ на адрес:
    ```
    {wallet_address}
    ```

    2. Сохраните скриншот или хэш транзакции

    3. Отправьте скриншот в этот чат

    *Внимание:* Отправляйте точную сумму!
    Платеж проверяется в течение 5-15 минут.
    """

    await callback.message.edit_text(
        payment_text,
        parse_mode="Markdown"
    )

    await state.set_state(PaymentStates.waiting_screenshot)
    await state.update_data(wallet_network=network, wallet_address=wallet_address)


@router.message(PaymentStates.waiting_screenshot, F.photo)
async def receive_screenshot(message: Message, state: FSMContext):
    data = await state.get_data()

    with SessionLocal() as session:
        order = session.query(Order).filter(Order.id == data.get("order_id")).first()
        if order:
            payment = Payment(
                order_id=order.id,
                amount=order.amount,
                crypto_network=data.get("wallet_network"),
                wallet_address=data.get("wallet_address"),
                screenshot_path=f"data/screenshots/{message.photo[-1].file_id}.jpg",
                status="pending",
                created_at=datetime.utcnow()
            )
            session.add(payment)
            session.commit()

    await message.answer(
        "✅ Скриншот получен! Платеж проверяется...\n"
        "Статус обновится в течение 5-15 минут.",
        reply_markup=kb.back_button()
    )

    # Уведомление админа
    admin_notification = f"""
    🆕 Новый платеж!

    Пользователь: @{message.from_user.username}
    Заказ: {order.order_id if order else 'N/A'}
    Сумма: {data.get('price', 0)}$
    Сеть: {data.get('wallet_network')}

    Проверить платеж: /admin
    """

    # Отправка админам
    for admin_id in config.ADMIN_IDS:
        try:
            await message.bot.send_message(admin_id, admin_notification)
        except:
            pass

    await state.clear()


@router.callback_query(F.data == "check_payment")
async def check_payment(callback: CallbackQuery):
    await callback.answer(
        "✅ Платеж проверяется... Статус обновится автоматически.",
        show_alert=True
    )