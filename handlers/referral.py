from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import keyboards as kb
from database import SessionLocal, User, Referral
import config

router = Router()


@router.message(F.text == "👥 Реферальная система")
@router.message(F.text == "Реферальная система 👤")
async def referral_system(message: Message):
    with SessionLocal() as session:
        user = session.query(User).filter(User.telegram_id == message.from_user.id).first()

        if not user:
            await message.answer("Сначала запустите бота командой /start")
            return

        referrals_count = session.query(User).filter(User.referrer_id == user.id).count()

        referral_text = f"""
        👥 *Реферальная система*

        @Brude_Seller_Bot

        ---
        *Зарабатывай с нашей реферальной программой!*

        Ваша персональная ссылка:
        https://t.me/{config.BOT_USERNAME}?start=ref{user.id}

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
@router.message(F.text == "Заработать 💰")
async def earn_money(message: Message):
    earn_text = """Приветствую тебя дорогой друг, хочешь заработать? Команда @Brude_Seller_Bot поможет тебе в этом 🐳

Что требуется от тебя? Все довольно просто и понятно, нам нужны новые клиенты за которых мы будем платить вам, в свою очередь вы будете лить нам данных клиентов

Какие условия? Вы получаете 15% от суммы, на которую закупит ваш реферал, приглашенный именно вами, эти 15% будут выдаваться аккаунтами

Добавление рефералов будет возможно только при общей стоимости ваших закупок на более чем 50$ 

Специально для вас мы наняли менеджера по трафику вот его контакты, просьба иметь уважение ко времени данного члена нашей команды"""

    await message.answer(
        earn_text,
        parse_mode="Markdown"
    )


@router.callback_query(F.data.startswith("copy_link:"))
async def copy_referral_link(callback: CallbackQuery):
    user_id = int(callback.data.split(":")[1])
    # Формируем ссылку с username бота (он должен быть получен при старте)
    link = f"https://t.me/{config.BOT_USERNAME}?start=ref{user_id}"
    await callback.answer(
        f"Ссылка скопирована: {link}",
        show_alert=True
    )