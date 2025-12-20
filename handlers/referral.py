from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import keyboards as kb
from database import SessionLocal, User, Referral
import config

router = Router()


@router.message(F.text == "👥 Реферальная система")
async def referral_system(message: Message):
    with SessionLocal() as session:
        user = session.query(User).filter(User.telegram_id == message.from_user.id).first()

        if not user:
            await message.answer("Сначала запустите бота командой /start")
            return

        # Подсчет рефералов
        referrals_count = session.query(User).filter(User.referrer_id == user.id).count()

        referral_text = f"""
        👥 *Реферальная система*

        @Venmo_Seller_Bot

        ---
        *Зарабатывай с нашей реферальной программой!*

        Ваша персональная ссылка:
        https://t.me/Venmo_Seller_Bot?start=ref{user.id}

        ---
        *Как это работает?*
        • Приглашаешь друзей – делись ссылкой
        • Они покупают – ты получаешь {config.REFERRAL_PERCENT}% от их заказа
        • Чем больше рефералов – тем выше доход!

        ---
        *Ваша статистика:*
        • Приглашено: {referrals_count} человек
        • Заработано: {user.balance}$

        ---
        *Начни привлекать клиентов прямо сейчас!*

        PS. 10 друзей = гарантированный профит!
        """

        await message.answer(
            referral_text,
            reply_markup=kb.referral_keyboard(user.id),
            parse_mode="Markdown",
            disable_web_page_preview=True
        )


@router.message(F.text == "💰 Заработать")
async def earn_money(message: Message):
    earn_text = """
    💰 *Заработать с нами!*

    @Venmo_Seller_Bot

    Команда @Venmo_Seller_Bot поможет тебе заработать! 💡

    *Что требуется от тебя?*
    Все просто: нам нужны новые клиенты, а мы платим тебе за их привлечение.

    *Условия:*
    • Вы получаете 15% от суммы покупок ваших рефералов
    • Выплаты производятся аккаунтами или на баланс
    • Добавление рефералов возможно при общей сумме ваших закупок от 50$

    *Контакты менеджера по трафику:*
    @VenmoSell_Manager

    Просьба уважать время нашего менеджера!
    """

    await message.answer(
        earn_text,
        parse_mode="Markdown"
    )


@router.callback_query(F.data.startswith("copy_link:"))
async def copy_referral_link(callback: CallbackQuery):
    link = callback.data.split(":")[1]
    await callback.answer(
        f"Ссылка скопирована: {link}",
        show_alert=True
    )