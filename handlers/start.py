from datetime import datetime
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
import config
from database import SessionLocal, User
import keyboards as kb

router = Router()


def get_or_create_user(telegram_id: int, username: str, full_name: str, referrer_id: int = None):
    with SessionLocal() as session:
        user = session.query(User).filter(User.telegram_id == telegram_id).first()
        if not user:
            # Генерация реферального кода
            import random
            import string
            referral_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

            user = User(
                telegram_id=telegram_id,
                username=username,
                full_name=full_name,
                referral_code=referral_code,
                referrer_id=referrer_id,
                created_at=datetime.utcnow()
            )
            session.add(user)
            session.commit()

            # Начисление бонуса рефереру
            if referrer_id:
                referrer = session.query(User).filter(User.id == referrer_id).first()
                if referrer:
                    referrer.balance += 10  # Бонус за приглашение
                    session.commit()

        return user


def create_welcome_keyboard():
    """Создает комбинированную клавиатуру для приветствия"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🛒 Купить аккаунты", callback_data="menu_buy"))
    builder.add(InlineKeyboardButton(text="🌐 Поддержка", callback_data="menu_support"))
    builder.add(InlineKeyboardButton(text="📢 Канал FAQ", url="https://t.me/Exxcomm"))  # Изменено с callback_data на url
    builder.add(InlineKeyboardButton(text="✅ Отзывы", url="https://t.me/brudesellerfb"))
    builder.add(InlineKeyboardButton(text="👤 Рефералка", callback_data="menu_referral"))
    builder.add(InlineKeyboardButton(text="💰 Заработать", callback_data="menu_earn"))
    builder.adjust(1, 2, 1, 1, 1)
    return builder.as_markup()

async def send_welcome_menu(message: Message):
    """Функция для отправки приветственного меню (работает на всех платформах)"""
    user_name = message.from_user.first_name or "друг"

    welcome_text = f"""👋 Привет, {user_name}!

Добро пожаловать в Brude Seller Bot ✨

Давно хотел приобрести качественные Venmo аккаунты с балансом? Тебе определенно к нам! ⭐️

Ниже располагается меню, ознакамливайся 🎲"""

    # Отправляем приветственное сообщение с inline кнопками
    await message.answer(
        welcome_text,
        parse_mode="HTML",
        reply_markup=create_welcome_keyboard()  # Используем inline клавиатуру
    )

@router.message(CommandStart())
async def cmd_start(message: Message):
    # Обработка реферальной ссылки
    referrer_id = None
    if len(message.text.split()) > 1:
        ref_code = message.text.split()[1]
        if ref_code.startswith('ref'):
            try:
                referrer_id = int(ref_code[3:])
            except ValueError:
                pass

    user = get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username or "",
        full_name=message.from_user.full_name or "",
        referrer_id=referrer_id
    )

    await send_welcome_menu(message)


@router.message(Command("menu"))
async def show_menu(message: Message):
    """Показ меню по команде /menu"""
    await send_welcome_menu(message)


@router.message(Command("help"))
@router.message(F.text == "🆘 Тех. Поддержка")
@router.message(F.text == "Поддержка 🌐")
async def support_handler(message: Message):
    support_text = """
🛎️ <b>Нужна помощь? Обращайся правильно!</b>
🔹 Твой номер обращения: <code>#776825</code>
🔹 Менеджер поддержки: @VenmoSell_Manager

📌 <b>Правила обращения:</b>
✅ Будь вежлив и точен – опиши проблему четко и без лишних сообщений.
✅ Не спрашивай о статусе чека – обработка занимает до 15 минут.
✅ Нет спаму! Одно подробное сообщение > 10 коротких.

🚀 <i>Мы решим вопрос быстро, если ты следуешь этим простым правилам.</i>

👉 Просто перешли этот номер (<code>#776825</code>) менеджеру – и жди ответа!

<b>P.S.</b> Чем точнее опишешь проблему, тем быстрее получишь решение. 😉

🔍 <b>Хочешь убедиться в нашей надежности?</b>
📢 Присоединяйся к нашему официальному каналу:
👉 <a href="https://t.me/brudesellerfb">Отзывы & Анонсы</a>

<b>Здесь ты найдешь:</b>
✅ Реальные отзывы покупателей с пруфами
✅ Акции и конкурсы с крутыми призами
✅ Свежие анонсы обновлений и спецпредложений

<b>Подпишись сейчас – не упусти выгоду!</b> 🎁

<b>P.S.</b> Все честно – мы ценим твое доверие! 😊
    """

    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_to_main"))
    keyboard.add(InlineKeyboardButton(text="🛒 Купить", callback_data="menu_buy"))
    keyboard.adjust(2)

    await message.answer(
        support_text,
        reply_markup=keyboard.as_markup(),
        parse_mode="HTML"
    )


@router.message(Command("reviews"))
@router.message(F.text == "✅ Удачные сделки")
@router.message(F.text == "Удачные сделки ✅")
async def successful_deals(message: Message):
    deals_text = """
 🔍 <b>Хочешь убедиться в нашей надежности?</b>
📢 Присоединяйся к нашему официальному каналу:
👉 <a href="https://t.me/brudesellerfb">Отзывы & Анонсы</a>

<b>Здесь ты найдешь:</b>
✅ Реальные отзывы покупателей с пруфами
✅ Акции и конкурсы с крутыми призами
✅ Свежие анонсы обновлений и спецпредложений

<b>Подпишись сейчас – не упусти выгоду!</b> 🎁

<b>P.S.</b> Все честно – мы ценим твое доверие! 😊
    """

    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_to_main"))
    keyboard.add(InlineKeyboardButton(text="Подписаться", url="https://t.me/brudesellerfb"))
    keyboard.adjust(2)

    await message.answer(
        deals_text,
        parse_mode="HTML",
        reply_markup=keyboard.as_markup(),
        disable_web_page_preview=True
    )


@router.message(F.text == "📊 FAQ")
@router.message(F.text == "FAQ")
@router.message(F.text == "FAQ ❓")
async def faq_handler(message: Message):
    faq_text = """
❓ <b>Часто задаваемые вопросы</b>

1. <b>Как происходит покупка?</b>
- Выбираете количество аккаунтов
- Оплачиваете через CryptoBot или криптовалюту
- Получаете товар после подтверждения платежа

2. <b>Сколько времени занимает доставка?</b>
- Мгновенно после подтверждения платежа (5-15 минут)

3. <b>Какие гарантии?</b>
- Полный возврат при нерабочем аккаунте
- Гарантия замены в течение 24 часов

4. <b>Как работает реферальная система?</b>
- Вы получаете 15% от суммы покупок ваших рефералов
- Выплаты аккаунтами или на баланс

5. <b>Как связаться с поддержкой?</b>
- Через меню "Тех. Поддержка"
- Напрямую менеджеру: @VenmoSell_Manager

📢 <b>Подпишитесь на наш канал для актуальной информации:</b>
👉 https://t.me/Exxcomm
    """

    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_to_main"))
    keyboard.add(InlineKeyboardButton(text="🌐 Поддержка", callback_data="menu_support"))
    keyboard.add(InlineKeyboardButton(text="📢 Канал", url="https://t.me/Exxcomm"))
    keyboard.adjust(1, 2, 1)

    await message.answer(faq_text, parse_mode="HTML", reply_markup=keyboard.as_markup())


@router.callback_query(F.data == "menu_faq")
async def menu_faq_handler(callback: CallbackQuery):
    """Обработчик кнопки 'FAQ' - сразу открывает канал"""
    # Создаем кнопку с ссылкой
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Перейти в канал", url="https://t.me/Exxcomm")]
    ])

    # Отправляем сообщение с ссылкой
    await callback.message.edit_text(
        "📢 <b>Нажмите кнопку ниже для перехода в канал:</b>",
        parse_mode="HTML",
        reply_markup=keyboard
    )
    await callback.answer()


@router.message(F.text.in_(["🏠 Главное меню", "Главное меню", "Меню", "Назад"]))
async def return_to_main_menu(message: Message):
    """Обработчик для возврата в главное меню"""
    await send_welcome_menu(message)


# Обработчики для inline кнопок меню (для веб-версии)
@router.callback_query(F.data == "menu_buy")
async def menu_buy_handler(callback: CallbackQuery):
    """Обработчик кнопки 'Купить аккаунты' из inline меню"""
    await callback.answer()
    # Удаляем старое сообщение
    await callback.message.delete()
    # Имитируем нажатие на кнопку меню
    from handlers.buy import buy_accounts
    await buy_accounts(callback.message)


@router.callback_query(F.data == "menu_support")
async def menu_support_handler(callback: CallbackQuery):
    """Обработчик кнопки 'Поддержка' из inline меню"""
    await callback.answer("Открываю поддержку...")

    try:
        # Сначала отправляем новое сообщение с поддержкой
        support_text = """
🛎️ <b>Нужна помощь? Обращайся правильно!</b>
🔹 Твой номер обращения: <code>#776825</code>
🔹 Менеджер поддержки: @VenmoSell_Manager

📌 <b>Правила обращения:</b>
✅ Будь вежлив и точен – опиши проблему четко и без лишних сообщений.
✅ Не спрашивай о статусе чека – обработка занимает до 15 минут.
✅ Нет спаму! Одно подробное сообщение > 10 коротких.

🚀 <i>Мы решим вопрос быстро, если ты следуешь этим простым правилам.</i>

👉 Просто перешли этот номер (<code>#776825</code>) менеджеру – и жди ответа!

<b>P.S.</b> Чем точнее опишешь проблему, тем быстрее получишь решение. 😉

🔍 <b>Хочешь убедиться в нашей надежности?</b>
📢 Присоединяйся к нашему официальному каналу:
👉 <a href="https://t.me/your_channel">Отзывы & Анонсы</a>
"""

        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_to_main"))
        keyboard.add(InlineKeyboardButton(text="🛒 Купить", callback_data="menu_buy"))
        keyboard.adjust(2)

        # Редактируем текущее сообщение
        await callback.message.edit_text(
            support_text,
            reply_markup=keyboard.as_markup(),
            parse_mode="HTML",
            disable_web_page_preview=True
        )

    except Exception as e:
        # Если не получилось отредактировать, отправляем новое сообщение
        await callback.message.answer(
            "Произошла ошибка. Попробуйте еще раз или используйте команду /support",
            reply_markup=kb.main_menu()
        )


@router.callback_query(F.data == "menu_faq")
async def menu_faq_handler(callback: CallbackQuery):
    """Обработчик кнопки 'FAQ' из inline меню"""
    await callback.answer()
    await callback.message.delete()
    callback.message.text = "FAQ ❓"
    await faq_handler(callback.message)


@router.callback_query(F.data == "menu_reviews")
async def menu_reviews_handler(callback: CallbackQuery):
    """Обработчик кнопки 'Удачные сделки' из inline меню"""
    await callback.answer()
    await callback.message.delete()
    callback.message.text = "Удачные сделки ✅"
    await successful_deals(callback.message)


@router.callback_query(F.data == "menu_referral")
async def menu_referral_handler(callback: CallbackQuery):
    """Упрощенный обработчик кнопки 'Рефералка'"""
    await callback.answer()

    referral_text = f"""
💰 <b>Реферальная система</b>

Приглашай друзей и получай бонусы!

🔹 <b>Твоя реферальная ссылка:</b>
<code>https://t.me/your_bot?start=ref{callback.from_user.id}</code>

🔹 <b>Как это работает:</b>
1. Делись своей ссылкой с друзьями
2. Когда друг переходит по ссылке и запускает бота - он становится твоим рефералом
3. За каждого друга ты получаешь <b>10$</b> на баланс
4. Твой друг получает <b>5% скидку</b> на первую покупку

📊 <b>Твоя статистика:</b>
• Приглашено друзей: <b>0</b>
• Заработано: <b>0$</b>
• Доступно к выводу: <b>0$</b>

💡 <b>Советы для заработка:</b>
• Делитесь ссылкой в тематических чатах
• Рассказывайте друзьям о преимуществах
• Получайте пассивный доход!

🔄 <b>Минимальная сумма вывода:</b> 50$
📞 <b>Для вывода:</b> Обратитесь к @VenmoSell_Manager
"""

    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="📋 Копировать ссылку", callback_data="copy_ref_link"))
    keyboard.add(InlineKeyboardButton(text="💰 Заработать", callback_data="menu_earn"))
    keyboard.add(InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_to_main"))
    keyboard.adjust(1, 2, 1)

    # Редактируем текущее сообщение
    await callback.message.edit_text(
        referral_text,
        reply_markup=keyboard.as_markup(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "menu_earn")
async def menu_earn_handler(callback: CallbackQuery):
    """Обработчик кнопки 'Заработать' из inline меню"""
    await callback.answer()
    await callback.message.delete()
    callback.message.text = "Заработать 💰"
    from handlers.referral import earn_money
    await earn_money(callback.message)