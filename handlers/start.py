from datetime import datetime

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.orm import Session

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


async def send_welcome_menu(message: Message):
    """Функция для отправки приветственного меню (работает на всех платформах)"""
    user_name = message.from_user.first_name or "друг"
    
    welcome_text = f"""👋 Привет, {user_name}!

Добро пожаловать в Brude Seller Bot ✨

Давно хотел приобрести качественные Venmo аккаунты с балансом? Тебе определенно к нам! ⭐️

Ниже располагается меню, ознакамливайся 🎲"""

    # Отправляем одно сообщение с reply keyboard (работает на мобильных и веб)
    await message.answer(
        welcome_text,
        parse_mode="HTML",
        reply_markup=kb.main_menu()
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
👉 <a href="https://t.me/your_channel">Отзывы & Анонсы</a>

<b>Здесь ты найдешь:</b>
✅ Реальные отзывы покупателей с пруфами
✅ Акции и конкурсы с крутыми призами
✅ Свежие анонсы обновлений и спецпредложений

<b>Подпишись сейчас – не упусти выгоду!</b> 🎁

<b>P.S.</b> Все честно – мы ценим твое доверие! 😊
    """

    await message.answer(
        support_text,
        reply_markup=kb.support_keyboard(),
        parse_mode="HTML"
    )


@router.message(Command("reviews"))
@router.message(F.text == "✅ Удачные сделки")
@router.message(F.text == "Удачные сделки ✅")
async def successful_deals(message: Message):
    deals_text = """
 🔍 <b>Хочешь убедиться в нашей надежности?</b>
📢 Присоединяйся к нашему официальному каналу:
👉 <a href="https://t.me/your_channel">Отзывы & Анонсы</a>

<b>Здесь ты найдешь:</b>
✅ Реальные отзывы покупателей с пруфами
✅ Акции и конкурсы с крутыми призами
✅ Свежие анонсы обновлений и спецпредложений

<b>Подпишись сейчас – не упусти выгоду!</b> 🎁

<b>P.S.</b> Все честно – мы ценим твое доверие! 😊
    """

    await message.answer(
        deals_text,
        parse_mode="HTML",
        disable_web_page_preview=True
    )


@router.message(F.text == "📊 FAQ")
@router.message(F.text == "FAQ")
@router.message(F.text == "FAQ ❓")
async def faq_handler(message: Message):
    faq_text = """
    ❓ *Часто задаваемые вопросы*

    1. *Как происходит покупка?*
    - Выбираете количество аккаунтов
    - Оплачиваете через CryptoBot или криптовалюту
    - Получаете товар после подтверждения платежа

    2. *Сколько времени занимает доставка?*
    - Мгновенно после подтверждения платежа (5-15 минут)

    3. *Какие гарантии?*
    - Полный возврат при нерабочем аккаунте
    - Гарантия замены в течение 24 часов

    4. *Как работает реферальная система?*
    - Вы получаете 15% от суммы покупок ваших рефералов
    - Выплаты аккаунтами или на баланс

    5. *Как связаться с поддержкой?*
    - Через меню "Тех. Поддержка"
    - Напрямую менеджеру: @VenmoSell_Manager
    """

    await message.answer(faq_text, parse_mode="Markdown")


@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    await callback.message.delete()
    await send_welcome_menu(callback.message)


@router.message(F.text.in_(["🏠 Главное меню", "Главное меню", "Меню", "Назад"]))
async def return_to_main_menu(message: Message):
    """Обработчик для возврата в главное меню"""
    await send_welcome_menu(message)


# Обработчики для inline кнопок меню (для веб-версии)
@router.callback_query(F.data == "menu_buy")
async def menu_buy_handler(callback: CallbackQuery):
    """Обработчик кнопки 'Купить аккаунты' из inline меню"""
    await callback.answer()
    # Имитируем нажатие на кнопку меню
    callback.message.text = "Купить аккаунты 🛒"
    from handlers.buy import buy_accounts
    await buy_accounts(callback.message)


@router.callback_query(F.data == "menu_support")
async def menu_support_handler(callback: CallbackQuery):
    """Обработчик кнопки 'Поддержка' из inline меню"""
    await callback.answer()
    callback.message.text = "Поддержка 🌐"
    await support_handler(callback.message)


@router.callback_query(F.data == "menu_faq")
async def menu_faq_handler(callback: CallbackQuery):
    """Обработчик кнопки 'FAQ' из inline меню"""
    await callback.answer()
    callback.message.text = "FAQ ❓"
    await faq_handler(callback.message)


@router.callback_query(F.data == "menu_reviews")
async def menu_reviews_handler(callback: CallbackQuery):
    """Обработчик кнопки 'Удачные сделки' из inline меню"""
    await callback.answer()
    callback.message.text = "Удачные сделки ✅"
    await successful_deals(callback.message)


@router.callback_query(F.data == "menu_referral")
async def menu_referral_handler(callback: CallbackQuery):
    """Обработчик кнопки 'Реферальная система' из inline меню"""
    await callback.answer()
    callback.message.text = "Реферальная система 👤"
    from handlers.referral import referral_system
    await referral_system(callback.message)


@router.callback_query(F.data == "menu_earn")
async def menu_earn_handler(callback: CallbackQuery):
    """Обработчик кнопки 'Заработать' из inline меню"""
    await callback.answer()
    callback.message.text = "Заработать 💰"
    from handlers.referral import earn_money
    await earn_money(callback.message)