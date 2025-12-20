from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import Session
from database import SessionLocal, User
import keyboards as kb
from datetime import datetime
import config

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


@router.message(CommandStart())
async def cmd_start(message: Message):
    # Обработка реферальной ссылки
    referrer_id = None
    if len(message.text.split()) > 1:
        ref_code = message.text.split()[1]
        if ref_code.startswith('ref'):
            try:
                referrer_id = int(ref_code[3:])
            except:
                pass

    user = get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name,
        referrer_id=referrer_id
    )

    welcome_text = """
    🏪 *Лучший магазин Venmo аккаунтов*

    ⚡️ Быстро | 💰 Выгодно | ✅ Надёжно

    *Бесплатно в течение недели:*
    • Помощь с выбором лучшего Venmo аккаунта
    • Гарантированная поддержка после покупки
    • Уникальные условия для вашего бизнеса

    👇 Выберите действие:
    """

    await message.answer(
        welcome_text,
        reply_markup=kb.main_menu(),
        parse_mode="Markdown"
    )


@router.message(F.text == "🆘 Тех. Поддержка")
async def support_handler(message: Message):
    support_text = """
    🛠 *Техническая поддержка*

    @Venmo_Seller_Bot

    ---
    *Нужна помощь? Обращайся правильно!*
    • Твой номер обращения: #939183
    • Менеджер поддержки: @VenmoSell_Manager

    ---
    *Правила обращения:*
    • Будь вежлив и точен – опиши проблему четко
    • Не спрашивай о статусе чека – обработка до 15 минут
    • Нет спаму! Одно подробное сообщение > 10 коротких

    ---
    *Мы решим вопрос быстро, если ты следуешь правилам!*

    **PS. Чем точнее опишешь проблему, тем быстрее получишь решение.**
    """

    await message.answer(
        support_text,
        reply_markup=kb.support_keyboard(),
        parse_mode="Markdown"
    )


@router.message(F.text == "✅ Удачные сделки")
async def successful_deals(message: Message):
    deals_text = """
    ✅ *Удачные сделки*

    @Venmo_Seller_Bot

    Хочешь убедиться в нашей надежности?
    Присоединяйся к официальному каналу:
    • Отзывы & Анонсы

    Здесь ты найдешь:
    • Реальные отзывы покупателей с пруфами
    • Акции и конкурсы с крутыми призами
    • Свежие анонсы обновлений и спецпредложений

    [Подпишись сейчас](https://t.me/reviews_channel) – не упусти выгоду!

    PS. Все честно – мы ценим твое доверие!
    """

    await message.answer(
        deals_text,
        parse_mode="Markdown",
        disable_web_page_preview=True
    )


@router.message(F.text == "📊 FAQ")
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
    await cmd_start(callback.message)