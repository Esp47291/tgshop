from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def main_menu():
    """Главное меню - работает на всех платформах (мобильная и веб-версия)"""
    builder = ReplyKeyboardBuilder()
    # Первая кнопка на всю ширину
    builder.add(KeyboardButton(text="Купить аккаунты 🛒"))
    # Вторая и третья кнопки рядом
    builder.add(KeyboardButton(text="Поддержка 🌐"))
    builder.add(KeyboardButton(text="FAQ ❓"))
    # Остальные по одной
    builder.add(KeyboardButton(text="Удачные сделки ✅"))
    builder.add(KeyboardButton(text="Реферальная система 👤"))
    builder.add(KeyboardButton(text="Заработать 💰"))
    # Настройка расположения: первая кнопка на всю ширину, затем 2 рядом, затем по одной
    builder.adjust(1, 2, 1, 1, 1)
    # Явно указываем параметры для совместимости с веб-версии
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Выберите действие из меню"
    )


def main_menu_inline():
    """Альтернативное inline меню для веб-версии"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🛒 Купить аккаунты", callback_data="menu_buy"))
    builder.add(InlineKeyboardButton(text="🌐 Поддержка", callback_data="menu_support"))
    builder.add(InlineKeyboardButton(text="❓ FAQ", callback_data="menu_faq"))
    builder.add(InlineKeyboardButton(text="✅ Удачные сделки", callback_data="menu_reviews"))
    builder.add(InlineKeyboardButton(text="👤 Рефералка", callback_data="show_referral"))  # Изменено callback_data
    builder.add(InlineKeyboardButton(text="💰 Заработать", callback_data="menu_earn"))
    builder.adjust(1, 2, 1, 1, 1)
    return builder.as_markup()


def create_welcome_keyboard():
    """Создает inline клавиатуру для приветственного сообщения"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🛒 Купить аккаунты", callback_data="menu_buy"))
    builder.add(InlineKeyboardButton(text="🌐 Поддержка", callback_data="menu_support"))
    builder.add(InlineKeyboardButton(text="❓ FAQ", callback_data="menu_faq"))
    builder.add(InlineKeyboardButton(text="✅ Отзывы", callback_data="menu_reviews"))
    builder.add(InlineKeyboardButton(text="👤 Рефералка", callback_data="show_referral"))  # Изменено callback_data
    builder.add(InlineKeyboardButton(text="💰 Заработать", callback_data="menu_earn"))
    builder.adjust(1, 2, 1, 1, 1)
    return builder.as_markup()


def referral_keyboard(user_id: int):
    """Клавиатура для реферальной системы"""
    builder = InlineKeyboardBuilder()

    # Реферальная ссылка
    ref_link = f"https://t.me/Brude_Seller_Bot?start=ref{user_id}"

    builder.add(InlineKeyboardButton(
        text="📋 Копировать ссылку",
        callback_data=f"copy_link:{ref_link}"
    ))
    builder.add(InlineKeyboardButton(
        text="💰 Заработать",
        callback_data="menu_earn"
    ))
    builder.add(InlineKeyboardButton(
        text="◀️ Назад в меню",
        callback_data="back_to_main"
    ))
    builder.add(InlineKeyboardButton(
        text="📞 Менеджер",
        url="https://t.me/VenmoSell_Manager"
    ))

    builder.adjust(2, 1, 1)
    return builder.as_markup()


# Остальные функции остаются без изменений
def back_button():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="« Вернуться назад", callback_data="back_to_main"))
    return builder.as_markup()


def buy_menu():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Lite Pack (1 аккаунт)", callback_data="pack_lite"))
    builder.add(InlineKeyboardButton(text="Starter Pack (3 аккаунта)", callback_data="pack_starter"))
    builder.add(InlineKeyboardButton(text="Smart Pack (5 аккаунтов)", callback_data="pack_smart"))
    builder.add(InlineKeyboardButton(text="Pro Pack (10 аккаунтов)", callback_data="pack_pro"))
    builder.add(InlineKeyboardButton(text="Premium Pack (20 аккаунтов)", callback_data="pack_premium"))
    builder.add(InlineKeyboardButton(text="Ultimate Pack (30 аккаунтов)", callback_data="pack_ultimate"))
    builder.add(InlineKeyboardButton(text="Свое количество", callback_data="custom_quantity"))
    builder.add(InlineKeyboardButton(text="« Вернуться назад", callback_data="back_to_main"))
    builder.adjust(1)
    return builder.as_markup()


def payment_methods():
    buttons = [
        [InlineKeyboardButton(text="💳 Криптовалюта", callback_data="payment_crypto")],
        [InlineKeyboardButton(text="🏦 Банковская карта", callback_data="payment_card")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_buy")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def cryptobot_payment():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="💳 Оплатить счет", callback_data="pay_invoice"))
    builder.add(InlineKeyboardButton(text="✅ Проверить оплату", callback_data="check_payment"))
    builder.add(InlineKeyboardButton(text="« Назад", callback_data="back_to_payment"))
    builder.adjust(1)
    return builder.as_markup()


def back_to_payment():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="« Назад к выбору оплаты", callback_data="back_to_payment"))
    return builder.as_markup()


def crypto_networks():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="USDT (TRC20)", callback_data="network_trc20"))
    builder.add(InlineKeyboardButton(text="USDT (BEP20)", callback_data="network_bep20"))
    builder.add(InlineKeyboardButton(text="TON", callback_data="network_ton"))
    builder.add(InlineKeyboardButton(text="ETH", callback_data="network_eth"))
    builder.add(InlineKeyboardButton(text="« Назад", callback_data="back_to_payment"))
    builder.adjust(2)
    return builder.as_markup()


def back_to_buy():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="« Назад к выбору количества", callback_data="back_to_buy"))
    return builder.as_markup()


def support_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="📝 Создать обращение", callback_data="create_ticket"))
    builder.add(InlineKeyboardButton(text="📞 Связаться с менеджером", url="https://t.me/BrudeSell_Manager"))
    builder.add(InlineKeyboardButton(text="📝 Оставить отзыв", callback_data="leave_review"))
    builder.add(InlineKeyboardButton(text="« Вернуться назад", callback_data="back_to_main"))
    builder.adjust(1)
    return builder.as_markup()


def admin_menu():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats"))
    builder.add(InlineKeyboardButton(text="👤 Пользователи", callback_data="admin_users"))
    builder.add(InlineKeyboardButton(text="📦 Заказы", callback_data="admin_orders"))
    builder.add(InlineKeyboardButton(text="💸 Платежи", callback_data="admin_payments"))
    builder.add(InlineKeyboardButton(text="🎁 Выдать товар", callback_data="admin_deliver"))
    builder.add(InlineKeyboardButton(text="✉️ Рассылка", callback_data="admin_broadcast"))
    builder.adjust(2)
    return builder.as_markup()