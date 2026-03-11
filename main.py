import asyncio
import logging
import os
import sys
import signal
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import config
from database import init_db
from handlers import start_router, buy_router, payments_router, support_router, referral_router, admin_router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("data/bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Создаём необходимые папки
os.makedirs("data", exist_ok=True)
os.makedirs("data/screenshots", exist_ok=True)


async def shutdown(bot: Bot):
    logger.info("Shutting down bot...")
    await bot.session.close()


async def main():
    # Инициализация базы данных
    init_db()

    # Логирование используемого токена (первые 20 символов для безопасности)
    token_preview = config.BOT_TOKEN[:20] + "..." if len(config.BOT_TOKEN) > 20 else config.BOT_TOKEN
    logger.info(f"Используется BOT_TOKEN: {token_preview} (из .env файла)")

    # Инициализация бота
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )

    # Получаем информацию о боте для username
    bot_info = await bot.get_me()
    config.BOT_USERNAME = bot_info.username
    logger.info(f"Bot username: @{config.BOT_USERNAME}")

    await bot.set_my_commands([
        BotCommand(command="start", description="Старт"),
        BotCommand(command="buy", description="Купить аккаунты"),
        BotCommand(command="help", description="Тех. Поддержка"),
        BotCommand(command="reviews", description="Отзывы"),
        BotCommand(command="faq", description="FAQ"),
    ])

    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Регистрация роутеров
    dp.include_router(start_router)
    dp.include_router(buy_router)
    dp.include_router(payments_router)
    dp.include_router(support_router)
    dp.include_router(referral_router)
    dp.include_router(admin_router)

    logger.info("Бот запущен!")

    # Обработка сигналов только для Unix-подобных систем
    if sys.platform != 'win32':
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown(bot)))

    # Запуск поллинга с корректным завершением
    try:
        await dp.start_polling(bot)
    finally:
        await shutdown(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен по команде пользователя")
    except Exception as e:
        logger.exception(f"Необработанная ошибка: {e}")