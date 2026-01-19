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

От 1 до 20 Штук - 10$💰
От 20 до 50 Штук - 9$💰
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
    # Получаем правильное название пакета с заглавной буквы
    package_key = package_type.capitalize()

    # Проверяем, что пакет существует
    if package_key not in config.PACKAGES:
        await callback.answer("❌ Пакет не найден", show_alert=True)
        return

    package = config.PACKAGES[package_key]

    await state.update_data(
        quantity=package["quantity"],
        price=float(package["price"]),
        package_type=package_key.lower()
    )

    confirm_text = f"""
    🛒 *Подтверждение заказа*

    Товар: Venmo Accounts
    Количество: {package['quantity']} шт
    Сумма: ${package['price']:.2f}

    Все верно? Выберите способ оплаты:
    """

    await callback.message.edit_text(
        confirm_text,
        reply_markup=kb.payment_methods(),
        parse_mode="Markdown"
    )
    await callback.answer()


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

        # Расчет цены с исправленными границами
        if 1 <= quantity <= 20:
            price_per = config.PRICES["1-20"]
        elif 21 <= quantity <= 50:  # Исправлено с 20 на 21
            price_per = config.PRICES["20-50"]
        elif quantity >= 51:  # Исправлено с > 50 на >= 51
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
        Цена за шт: ${price_per:.2f}
        Сумма: ${total_price:.2f}

        Все верно? Выберите способ оплаты:
        """

        await message.answer(
            confirm_text,
            reply_markup=kb.payment_methods(),  # Убедитесь, что здесь есть кнопка "назад"
            parse_mode="Markdown"
        )
        # НЕ очищаем состояние здесь - это важно для кнопки "назад"
        # await state.clear()  # УДАЛИТЬ ЭТУ СТРОКУ!

    except ValueError:
        await message.answer("❌ Пожалуйста, введите корректное число!")


@router.callback_query(F.data == "back_to_buy")
async def back_to_buy_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()  # Очищаем состояние при возврате в меню
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

От 1 до 20 Штук - 10$💰
От 20 до 50 Штук - 9$💰
От 50 до 100 Штук - 8$💰

Нажми на кнопку свое кол-во чтобы приобрести аккаунты либо выбери из готовых паков
    """

    await callback.message.edit_text(
        buy_text,
        reply_markup=kb.buy_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_payment")
async def back_to_payment_methods(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    # Проверяем, есть ли данные в состоянии
    if not data:
        await callback.answer("❌ Данные заказа не найдены. Начните заново.", show_alert=True)
        # Возвращаем в меню покупки
        await back_to_buy_menu(callback, state)
        return

    # Форматируем цену
    quantity = data.get('quantity', 1)
    price = float(data.get('price', 10))

    # Для кастомного заказа показываем цену за штуку
    if data.get('package_type') == 'custom':
        # Рассчитываем цену за штуку
        if 1 <= quantity <= 20:
            price_per = config.PRICES["1-20"]
        elif 21 <= quantity <= 50:
            price_per = config.PRICES["20-50"]
        elif quantity >= 51:
            price_per = config.PRICES["50-100"]

        payment_text = f"""
        🛒 *Подтверждение заказа*

        Товар: Venmo Accounts
        Количество: {quantity} шт
        Цена за шт: ${price_per:.2f}
        Сумма: ${price:.2f}

        Все верно? Выберите способ оплаты:
        """
    else:
        # Для готовых пакетов
        payment_text = f"""
        🛒 *Подтверждение заказа*

        Товар: Venmo Accounts
        Количество: {quantity} шт
        Сумма: ${price:.2f}

        Все верно? Выберите способ оплаты:
        """

    await callback.message.edit_text(
        payment_text,
        reply_markup=kb.payment_methods(),  # Убедитесь, что клавиатура содержит кнопку "назад"
        parse_mode="Markdown"
    )
    await callback.answer()