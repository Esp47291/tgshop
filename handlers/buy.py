from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import keyboards as kb
import config
from database import SessionLocal, Order, User
from datetime import datetime
import random

router = Router()


class BuyStates(StatesGroup):
    choosing_quantity = State()
    choosing_package = State()
    custom_quantity = State()
    confirm_order = State()


@router.message(F.text == "🛒 Купить аккаунты")
async def buy_accounts(message: Message):
    buy_text = """
    🛍 *Купить аккаунты*

    @Venmo_Seller_Bot

    *Шаг 1 из 3... Выбор количества*

    **Решил купить аккаунты? Ты на верном пути!**
    Наши преимущества:

    • Гарантируем возврат в случае проблемы
    • Платежные системы высшего уровня
    • Удобные способы оплаты
    • Быстрая техподдержка 24/7

    ---

    *Прайс-лист:*
    • 1-20 шт: 105$/шт
    • 20-50 шт: 95$/шт
    • 50-100 шт: 85$/шт

    Выбери готовый пакет или укажи своё количество:
    """

    await message.answer(
        buy_text,
        reply_markup=kb.buy_menu(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data.startswith("pack_"))
async def choose_package(callback: CallbackQuery, state: FSMContext):
    package_type = callback.data.split("_")[1]
    package = config.PACKAGES[package_type.capitalize()]

    await state.update_data(
        quantity=package["quantity"],
        price=package["price"],
        package_type=package_type
    )

    confirm_text = f"""
    🛒 *Подтверждение заказа*

    Товар: Venmo Accounts
    Количество: {package['quantity']} шт
    Сумма: {package['price']}$

    Все верно? Выберите способ оплаты:
    """

    await callback.message.edit_text(
        confirm_text,
        reply_markup=kb.payment_methods(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "custom_quantity")
async def custom_quantity(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "✏️ *Введите желаемое количество аккаунтов:*",
        parse_mode="Markdown"
    )
    await state.set_state(BuyStates.custom_quantity)


@router.message(BuyStates.custom_quantity)
async def process_quantity(message: Message, state: FSMContext):
    try:
        quantity = int(message.text)
        if quantity < 1:
            raise ValueError

        # Расчет цены
        if 1 <= quantity <= 20:
            price_per = config.PRICES["1-20"]
        elif 20 <= quantity <= 50:
            price_per = config.PRICES["20-50"]
        elif quantity > 50:
            price_per = config.PRICES["50-100"]
        else:
            price_per = config.PRICES["1-20"]

        total_price = price_per * quantity

        await state.update_data(
            quantity=quantity,
            price=total_price,
            package_type="custom"
        )

        confirm_text = f"""
        🛒 *Подтверждение заказа*

        Товар: Venmo Accounts
        Количество: {quantity} шт
        Цена за шт: {price_per}$
        Сумма: {total_price}$

        Все верно? Выберите способ оплаты:
        """

        await message.answer(
            confirm_text,
            reply_markup=kb.payment_methods(),
            parse_mode="Markdown"
        )
        await state.clear()

    except ValueError:
        await message.answer("❌ Пожалуйста, введите корректное число!")


@router.callback_query(F.data == "back_to_buy")
async def back_to_buy_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    buy_text = """
    🛍 *Купить аккаунты*

    @Venmo_Seller_Bot

    *Шаг 1 из 3... Выбор количества*

    **Решил купить аккаунты? Ты на верном пути!**
    Наши преимущества:

    • Гарантируем возврат в случае проблемы
    • Платежные системы высшего уровня
    • Удобные способы оплаты
    • Быстрая техподдержка 24/7

    ---

    *Прайс-лист:*
    • 1-20 шт: 105$/шт
    • 20-50 шт: 95$/шт
    • 50-100 шт: 85$/шт

    Выбери готовый пакет или укажи своё количество:
    """

    await callback.message.edit_text(
        buy_text,
        reply_markup=kb.buy_menu(),
        parse_mode="Markdown"
    )


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