"""
Скрипт для проверки конфигурации бота
Запустите: python check_config.py
"""
import os
import sys
from dotenv import load_dotenv

# Исправление кодировки для Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("="*60)
print("ПРОВЕРКА КОНФИГУРАЦИИ БОТА")
print("="*60)

# Загрузка .env
load_dotenv()

# Проверка BOT_TOKEN
bot_token = os.getenv("BOT_TOKEN", "").strip()
print("\n1. BOT_TOKEN:")
if not bot_token or bot_token in ["YOUR_BOT_TOKEN_HERE", "your_bot_token_here"]:
    print("   ❌ НЕ УСТАНОВЛЕН")
    print("   📝 Действие: Откройте файл .env и замените YOUR_BOT_TOKEN_HERE на ваш токен от @BotFather")
else:
    print(f"   ✅ Установлен: {bot_token[:20]}...")
    if ":" in bot_token:
        print("   ✅ Формат токена правильный")
    else:
        print("   ⚠️  Формат токена может быть неправильным (должен содержать ':')")

# Проверка ADMIN_IDS
admin_ids_str = os.getenv("ADMIN_IDS", "").strip()
print("\n2. ADMIN_IDS:")
if not admin_ids_str or admin_ids_str in ["YOUR_ADMIN_ID_HERE", "your_admin_id_here"]:
    print("   ❌ НЕ УСТАНОВЛЕН")
    print("   📝 Действие: Откройте файл .env и замените YOUR_ADMIN_ID_HERE на ваш ID от @userinfobot")
else:
    try:
        admin_ids = [int(id.strip()) for id in admin_ids_str.split(',')]
        print(f"   ✅ Установлен: {admin_ids}")
    except ValueError:
        print(f"   ❌ Неверный формат: {admin_ids_str}")
        print("   📝 Действие: Используйте числа через запятую (например: 123456789)")

# Проверка CRYPTOBOT_TOKEN
cryptobot_token = os.getenv("CRYPTOBOT_TOKEN", "").strip()
print("\n3. CRYPTOBOT_TOKEN:")
if not cryptobot_token:
    print("   ⚠️  Не установлен (опционально)")
    print("   📝 Если хотите использовать CryptoBot, получите токен на @CryptoBot")
else:
    print(f"   ✅ Установлен: {cryptobot_token[:20]}...")

print("\n" + "="*60)
if not bot_token or bot_token in ["YOUR_BOT_TOKEN_HERE", "your_bot_token_here"]:
    print("❌ БОТ НЕ МОЖЕТ БЫТЬ ЗАПУЩЕН!")
    print("   Исправьте ошибки выше и попробуйте снова.")
else:
    print("✅ Основные настройки в порядке!")
    if not admin_ids_str or admin_ids_str in ["YOUR_ADMIN_ID_HERE", "your_admin_id_here"]:
        print("⚠️  Админ-панель будет недоступна без ADMIN_IDS")
print("="*60)
