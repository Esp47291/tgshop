"""
Конфигурационный файл бота
Все настройки можно изменить через переменные окружения (.env файл)
"""
import os
from dotenv import load_dotenv

# Загрузка переменных окружения с перезаписью существующих значений
# override=True гарантирует, что значения из .env всегда будут использоваться
# Это важно для обновления токена без перезапуска интерпретатора
load_dotenv(override=True)

# Токены и API ключи
# Чтение напрямую из .env файла для гарантии актуальности
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

# Проверка токена
if not BOT_TOKEN or BOT_TOKEN in ["YOUR_BOT_TOKEN_HERE", "", "your_bot_token_here"]:
    print("\n" + "="*60)
    print("❌ ОШИБКА: BOT_TOKEN не установлен!")
    print("="*60)
    print("\nЧтобы исправить:")
    print("1. Откройте файл .env в корне проекта")
    print("2. Найдите строку: BOT_TOKEN=YOUR_BOT_TOKEN_HERE")
    print("3. Замените YOUR_BOT_TOKEN_HERE на ваш реальный токен от @BotFather")
    print("\nПример:")
    print("BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz")
    print("\n" + "="*60 + "\n")
    raise ValueError("BOT_TOKEN не установлен! Откройте файл .env и укажите ваш токен от @BotFather")

CRYPTOBOT_TOKEN = os.getenv("CRYPTOBOT_TOKEN", "")  # Опционально, если не используется CryptoBot

# Администраторы (через запятую)
ADMIN_IDS_STR = os.getenv("ADMIN_IDS", "").strip()
if ADMIN_IDS_STR and ADMIN_IDS_STR not in ["YOUR_ADMIN_ID_HERE", "your_admin_id_here"]:
    try:
        ADMIN_IDS = [int(admin_id.strip()) for admin_id in ADMIN_IDS_STR.split(',')]
    except ValueError:
        ADMIN_IDS = []
        print("⚠️ ВНИМАНИЕ: Неверный формат ADMIN_IDS! Используйте числа через запятую (например: 123456789,987654321)")
else:
    ADMIN_IDS = []
    print("⚠️ ВНИМАНИЕ: ADMIN_IDS не установлен! Админ-панель будет недоступна")
    print("   Чтобы исправить: откройте .env и замените YOUR_ADMIN_ID_HERE на ваш ID от @userinfobot")

# ID менеджера поддержки (может быть username с @ или числовой ID)
SUPPORT_MANAGER_ID = os.getenv("SUPPORT_MANAGER_ID", "@VenmoSell_Manager")

# ID канала с отзывами
CHANNEL_ID = os.getenv("CHANNEL_ID", "@reviews_channel")

# Криптокошельки для приема платежей
WALLETS = {
    "USDT_TRC20": os.getenv("USDT_TRC20", ""),
    "USDT_BEP20": os.getenv("USDT_BEP20", ""),
    "TON": os.getenv("TON", ""),
    "USDT_TON": os.getenv("USDT_TON", ""),
    "ETH": os.getenv("ETH", "")
}

# Цены за единицу товара в зависимости от количества
PRICES = {
    "1-20": float(os.getenv("PRICE_1_20", "10")),
    "20-50": float(os.getenv("PRICE_20_50", "9")),
    "50-100": float(os.getenv("PRICE_50_100", "8"))
}

# Готовые пакеты товаров
PACKAGES = {
    "Lite": {
        "quantity": int(os.getenv("PACK_LITE_QTY", "1")),
        "price": float(os.getenv("PACK_LITE_PRICE", "10"))
    },
    "Starter": {
        "quantity": int(os.getenv("PACK_STARTER_QTY", "3")),
        "price": float(os.getenv("PACK_STARTER_PRICE", "30"))
    },
    "Smart": {
        "quantity": int(os.getenv("PACK_SMART_QTY", "5")),
        "price": float(os.getenv("PACK_SMART_PRICE", "50"))
    },
    "Pro": {
        "quantity": int(os.getenv("PACK_PRO_QTY", "10")),
        "price": float(os.getenv("PACK_PRO_PRICE", "100"))
    },
    "Premium": {
        "quantity": int(os.getenv("PACK_PREMIUM_QTY", "20")),
        "price": float(os.getenv("PACK_PREMIUM_PRICE", "1800"))
    },
    "Ultimate": {
        "quantity": int(os.getenv("PACK_ULTIMATE_QTY", "30")),
        "price": float(os.getenv("PACK_ULTIMATE_PRICE", "2700"))
    }
}

# Настройки базы данных
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/bot_database.db")

# Процент реферальной системы (от суммы покупки реферала)
REFERRAL_PERCENT = float(os.getenv("REFERRAL_PERCENT", "15"))

# Название товара (можно изменить)
PRODUCT_NAME = os.getenv("PRODUCT_NAME", "Venmo Accounts")

# Настройки логирования
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "data/bot.log")
