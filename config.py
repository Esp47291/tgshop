import os
from dotenv import load_dotenv

load_dotenv(override=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
IMAGES_DIR = os.path.join(DATA_DIR, "images")

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

print(f"BOT_TOKEN (первые 10 символов): {BOT_TOKEN[:10]}...")
print(f"Длина токена: {len(BOT_TOKEN)}")

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

CRYPTOBOT_TOKEN = os.getenv("CRYPTOBOT_TOKEN", "")

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

SUPPORT_MANAGER_ID = os.getenv("5324231382", "@exxzest")
CHANNEL_ID = os.getenv("-1002377898890", "@brudesellerfb")

WALLETS = {
    "USDT_TRC20": os.getenv("USDT_TRC20", ""),
    "USDT_BEP20": os.getenv("USDT_BEP20", ""),
    "TON": os.getenv("TON", ""),
    "USDT_TON": os.getenv("USDT_TON", ""),
    "ETH": os.getenv("ETH", "")
}

PRICES = {
    "1-19": float(os.getenv("PRICE_1_20", "10")),
    "20-49": float(os.getenv("PRICE_20_50", "9")),
    "50-100": float(os.getenv("PRICE_50_100", "8"))
}

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
        "price": float(os.getenv("PACK_PREMIUM_PRICE", "180"))
    },
    "Ultimate": {
        "quantity": int(os.getenv("PACK_ULTIMATE_QTY", "30")),
        "price": float(os.getenv("PACK_ULTIMATE_PRICE", "270"))
    }
}

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/bot_database.db")
REFERRAL_PERCENT = float(os.getenv("REFERRAL_PERCENT", "15"))
PRODUCT_NAME = os.getenv("PRODUCT_NAME", "Brude accounts")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "data/bot.log")

# Добавляем переменную для username бота (будет заполнена при запуске)
BOT_USERNAME ="Brude_Seller_Bot"

START_MENU_FILE_ID = os.getenv("START_MENU_FILE_ID", "")
SUPPORT_MENU_FILE_ID = os.getenv("SUPPORT_MENU_FILE_ID", "")
BUY_MENU_FILE_ID = os.getenv("BUY_MENU_FILE_ID", "")
PAYMENT_MENU_FILE_ID = os.getenv("PAYMENT_MENU_FILE_ID", "")

START_MENU_IMAGE = os.getenv("START_MENU_IMAGE", os.path.join(IMAGES_DIR, "start_menu.png"))
SUPPORT_MENU_IMAGE = os.getenv("SUPPORT_MENU_IMAGE", os.path.join(IMAGES_DIR, "support_menu.png"))
BUY_MENU_IMAGE = os.getenv("BUY_MENU_IMAGE", os.path.join(IMAGES_DIR, "buy_menu.png"))
PAYMENT_MENU_IMAGE = os.getenv("PAYMENT_MENU_IMAGE", os.path.join(IMAGES_DIR, "payment_menu.png"))