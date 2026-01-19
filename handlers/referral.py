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

        # Подсчет рефералов и их общего оборота
        referrals_count = session.query(User).filter(User.referrer_id == user.id).count()

        # Получаем всех рефералов
        referrals = session.query(User).filter(User.referrer_id == user.id).all()
        total_earnings = user.balance

        referral_text = f"""
💰 <b>РЕФЕРАЛЬНАЯ СИСТЕМА</b>

🎯 <b>Приглашай друзей и зарабатывай!</b>

🔗 <b>Твоя реферальная ссылка:</b>
<code>https://t.me/Brude_Seller_Bot?start=ref{user.id}</code>

📊 <b>Твоя статистика:</b>
├─ Приглашено друзей: <b>{referrals_count}</b>
├─ Заработано: <b>{total_earnings}$</b>
└─ Доступно к выводу: <b>{total_earnings}$</b>

🏆 <b>Условия программы:</b>
┌─ За каждого друга: <b>+{config.REFERRAL_PERCENT}%</b> от их покупок
├─ Минимальный вывод: <b>50$</b>
├─ Выплаты: <b>ежедневно</b>
└─ Способ выплат: <b>аккаунтами</b>

💡 <b>Как работает:</b>
1. Делишься своей ссылкой с друзьями
2. Они переходят и регистрируются по ней
3. Когда они покупают аккаунты - ты получаешь {config.REFERRAL_PERCENT}% от суммы их покупок
4. Выводишь заработанное на баланс!

🚀 <b>Пример заработка:</b>
• 10 друзей = ~100-500$ в месяц
• 50 друзей = ~500-2500$ в месяц
• 100 друзей = ~1000-5000$ в месяц

📈 <b>Советы для успеха:</b>
• Рассказывай о качестве наших аккаунтов
• Показывай реальные отзывы и доказательства
• Помогай новичкам разобраться

💬 <b>Вопросы?</b> Пиши: @BrudeSell_Manager

⚡️ <b>Начни зарабатывать прямо сейчас!</b>
"""

        await message.answer(
            referral_text,
            reply_markup=kb.referral_keyboard(user.id),
            parse_mode="HTML",
            disable_web_page_preview=True
        )



@router.message(F.text == "💰 Заработать")
@router.message(F.text == "Заработать 💰")
async def earn_money(message: Message):
    earn_text = """
💼 <b>ХОЧЕШЬ ЗАРАБАТЫВАТЬ С НАМИ?</b>

Команда @Brude_Seller_Bot поможет тебе в этом! 🐳

🎯 <b>Что требуется от тебя?</b>
Все довольно просто и понятно:
• Нам нужны новые клиенты
• Ты привлекаешь их к нам
• Мы платим тебе за каждого клиента

💰 <b>Условия сотрудничества:</b>
• Вы получаете <b>15%</b> от суммы закупок вашего реферала
• Выплаты производятся <b>аккаунтами Venmo</b>
• Рефералы добавляются при ваших закупках от <b>50$</b>

📊 <b>Пример расчёта:</b>
Если ваш реферал купил на 1000$:
• Ваша прибыль: <b>150$</b> в эквиваленте аккаунтов

👥 <b>Кто может стать партнёром?</b>
• Любой наш клиент с покупками от 50$
• Трафик-менеджеры
• Владельцы каналов и чатов
• Активные пользователи

📱 <b>Контакты менеджера по трафику:</b>
@BrudeSell_Manager

🚀 <b>Начни зарабатывать уже сегодня!</b>
Просто напиши менеджеру и начни привлекать клиентов.
"""

    # Кнопки для удобства
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="📞 Написать менеджеру", url="https://t.me/BrudeSell_Manager"))
    keyboard.add(InlineKeyboardButton(text="👥 Реферальная система", callback_data="menu_referral"))
    keyboard.adjust(1)

    await message.answer(
        earn_text,
        parse_mode="HTML",
        reply_markup=keyboard.as_markup()
    )


# Добавляем новый обработчик для inline кнопки рефералки
@router.callback_query(F.data == "menu_referral")
async def inline_referral_handler(callback: CallbackQuery):
    """Обработчик inline кнопки '👤 Рефералка'"""
    await callback.answer()

    # Создаем новое сообщение с текстом как у рефералки
    callback.message.text = "Реферальная система 👤"
    await referral_system(callback.message)