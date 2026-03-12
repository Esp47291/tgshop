from datetime import datetime
import random
import string

from aiogram import F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy.orm import Session

import config
from database import SessionLocal, User
import keyboards as kb
from utils.media_utils import resolve_photo_source

router = Router()


class DebugStates(StatesGroup):
    waiting_file_id_photo = State()


async def answer_with_inline_menu(message: Message, text: str, parse_mode: str = "HTML"):
    await message.answer(
        text,
        parse_mode=parse_mode,
        reply_markup=kb.main_menu_inline()
    )


def generate_unique_code(session):
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        if not session.query(User).filter(User.referral_code == code).first():
            return code


def get_or_create_user(telegram_id: int, username: str, full_name: str, referrer_id: int = None):
    with SessionLocal() as session:
        user = session.query(User).filter(User.telegram_id == telegram_id).first()
        if not user:
            # Проверяем, существует ли реферер
            if referrer_id:
                referrer = session.query(User).filter(User.id == referrer_id).first()
                if not referrer:
                    referrer_id = None  # игнорируем невалидный referrer_id

            referral_code = generate_unique_code(session)

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

            # Бонус за регистрацию убран, так как не соответствует описанию
            # Если нужен, можно добавить config.REFERRAL_REG_BONUS

        return user


async def send_welcome_menu(message: Message):
    user_name = message.from_user.first_name or "друг"

    welcome_text = f"""👋 Привет, {user_name}!

Добро пожаловать в Brude Seller Bot ✨

Давно хотел приобрести качественные Venmo аккаунты с балансом? Тебе определенно к нам! ⭐️

Ниже располагается меню, ознакамливайся 🎲"""

    await message.answer_photo(
        photo=resolve_photo_source(config.START_MENU_FILE_ID, config.START_MENU_IMAGE),
        caption=welcome_text,
        parse_mode="HTML",
        reply_markup=kb.main_menu_inline(),
        request_timeout=180
    )


@router.message(CommandStart())
async def cmd_start(message: Message):
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


@router.message(Command("cancel"), StateFilter("*"))
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        await answer_with_inline_menu(message, "Нет активного действия.")
        return
    await state.clear()
    await answer_with_inline_menu(message, "Действие отменено.")


@router.message(Command("help"))
@router.message(F.text == "🆘 Тех. Поддержка")
@router.message(F.text == "Поддержка 🌐")
async def support_handler(message: Message):
    support_text = """
🛎️ <b>Нужна помощь? Обращайся правильно!</b>
🔹 Твой номер обращения: <code>#776825</code>
🔹 Менеджер поддержки: @Exxzest

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

    await message.answer_photo(
        photo=resolve_photo_source(config.SUPPORT_MENU_FILE_ID, config.SUPPORT_MENU_IMAGE),
        caption=support_text,
        reply_markup=kb.support_keyboard(),
        parse_mode="HTML",
        request_timeout=180
    )


@router.message(Command("faq"))
async def faq_command_handler(message: Message):
    await message.answer(
        "FAQ | ПРАВИЛА",
        reply_markup=kb.faq_channel_button(),
        disable_web_page_preview=True
    )


@router.message(Command("fileid"))
async def fileid_command_handler(message: Message, state: FSMContext):
    if message.from_user.id not in config.ADMIN_IDS:
        return

    await state.set_state(DebugStates.waiting_file_id_photo)
    await message.answer(
        "Отправь следующим сообщением одну фотографию, и я верну ее `file_id`.",
        parse_mode="Markdown"
    )


@router.message(DebugStates.waiting_file_id_photo, F.photo)
async def fileid_photo_handler(message: Message, state: FSMContext):
    if message.from_user.id not in config.ADMIN_IDS:
        await state.clear()
        return

    photo = message.photo[-1]
    await message.answer(
        f"file_id:\n{photo.file_id}\n\nfile_unique_id:\n{photo.file_unique_id}",
        parse_mode=None
    )
    await state.clear()


@router.message(DebugStates.waiting_file_id_photo)
async def fileid_invalid_message_handler(message: Message):
    if message.from_user.id not in config.ADMIN_IDS:
        return

    await message.answer("Нужно отправить именно фото.")


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

    await message.answer(
        deals_text,
        parse_mode="HTML",
        disable_web_page_preview=True
    )


@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    await callback.message.delete()
    await send_welcome_menu(callback.message)


@router.message(F.text.in_(["🏠 Главное меню", "Главное меню", "Меню", "Назад"]))
async def return_to_main_menu(message: Message):
    await send_welcome_menu(message)


@router.callback_query(F.data == "menu_buy")
async def menu_buy_handler(callback: CallbackQuery):
    await callback.answer()
    from handlers.buy import buy_accounts
    await buy_accounts(callback.message)


@router.callback_query(F.data == "menu_support")
async def menu_support_handler(callback: CallbackQuery):
    await callback.answer()
    await support_handler(callback.message)


@router.callback_query(F.data == "menu_reviews")
async def menu_reviews_handler(callback: CallbackQuery):
    await callback.answer()
    await successful_deals(callback.message)


@router.callback_query(F.data == "menu_referral")
async def menu_referral_handler(callback: CallbackQuery):
    await callback.answer()
    from handlers.referral import referral_system
    await referral_system(callback.message)


@router.callback_query(F.data == "menu_earn")
async def menu_earn_handler(callback: CallbackQuery):
    await callback.answer()
    from handlers.referral import earn_money
    await earn_money(callback.message)