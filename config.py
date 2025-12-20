import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CRYPTOBOT_TOKEN = os.getenv("CRYPTOBOT_TOKEN", "")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "123456789").split(',')))
SUPPORT_MANAGER_ID = os.getenv("SUPPORT_MANAGER_ID", "@VenmoSell_Manager")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@reviews_channel")

# Криптокошельки
WALLETS = {
    "USDT_TRC20": os.getenv("USDT_TRC20", "THA≤xSV2D8R9F21fmXUqHpBQuHDwa6jotQ"),
    "USDT_BEP20": os.getenv("USDT_BEP20", "0x1385c0f58dEc3901349808461f0dc7a31e11f90"),
    "USDT_TON": os.getenv("USDT_TON", "UQBFCkkZesbxh9-rrIPx5gTsLeQ1Q3bL1azglig-JfXW71Uni"),
    "TON": os.getenv("TON", "UQBFCkkZesbxh9-rrIPx5gTsLeQ1Q3bL1azglig-JfXW71Uni"),
    "ETH": os.getenv("ETH", "0xA4b32ab8f838fc6b8b0a813a70ff6Ebf98836A3C")
}

# Цены
PRICES = {
    "1-20": 105,
    "20-50": 95,
    "50-100": 85
}

# Пакеты
PACKAGES = {
    "Lite": {"quantity": 1, "price": 105},
    "Starter": {"quantity": 3, "price": 315},
    "Smart": {"quantity": 5, "price": 525},
    "Pro": {"quantity": 10, "price": 1050},
    "Premium": {"quantity": 20, "price": 2100},
    "Ultimate": {"quantity": 30, "price": 3150}
}

DATABASE_URL = "sqlite:///data/bot_database.db"
REFERRAL_PERCENT = 15  # Процент реферальной системы