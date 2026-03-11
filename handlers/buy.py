from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
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


@router.message(Command("buy"))
@router.message(F.text == "🛒 Купить аккаунты")
@router.message(F.text == "Купить аккаунты 🛒")
async def buy_accounts(message: Message):
    buy_text = """
    Шаг 1 из 3... Выбор количества для покупки

Решил купить аккаунты? Ты на верном пути! ✈️
Наши преимущества перед другими сервисами: 

- Мы гарантируем возврат в случаи невалидности 🔮
- Готовы предоставить платежные системы высшего уровня 💾
- Удобные способы оплаты 📥
- Быстрая тех поддержка, готовая вам помочь в любой момент 📞

Кхм, перейдем к количеству 
Вот прайс лист на аккаунты💎

От 1 до 19 Штук - 10$💰
От 20 до 49 Штук - 9$💰
От 50 до 100 Штук - 8$💰

Нажми на кнопку свое кол-во чтобы приобрести аккаунты либо выбери из готовых паков
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

        if 1 <= quantity <= 19:
            price_per = config.PRICES["1-19"]
        elif 20 <= quantity <= 49:
            price_per = config.PRICES["20-49"]
        elif quantity >= 50:
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
        # НЕ очищаем state, так как данные ещё нужны для оплаты
        # await state.clear()  # УДАЛЕНО

    except ValueError:
        await message.answer("❌ Пожалуйста, введите корректное число!")


@router.callback_query(F.data == "back_to_buy")
async def back_to_buy_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    buy_text = """
    Шаг 1 из 3... Выбор количества для покупки

Решил купить аккаунты? Ты на верном пути! ✈️
Наши преимущества перед другими сервисами: 

- Мы гарантируем возврат в случаи невалидности 🔮
- Готовы предоставить платежные системы высшего уровня 💾
- Удобные способы оплаты 📥
- Быстрая тех поддержка, готовая вам помочь в любой момент 📞

Кхм, перейдем к количеству 
Вот прайс лист на аккаунты💎

От 1 до 19 Штук - 10$💰
От 20 до 49 Штук - 9$💰
От 50 до 100 Штук - 8$💰

Нажми на кнопку свое кол-во чтобы приобрести аккаунты либо выбери из готовых паков
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
    Сумма: {data.get('price', 10)}$

    Все верно? Выберите способ оплаты:
    """

    await callback.message.edit_text(
        payment_text,
        reply_markup=kb.payment_methods(),
        parse_mode="Markdown"
    )