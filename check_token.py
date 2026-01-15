"""
Скрипт для проверки токена из .env файла
Запустите: python check_token.py
"""
import os
import sys
from dotenv import load_dotenv

# Исправление кодировки для Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Загрузка с перезаписью
load_dotenv(override=True)

token = os.getenv("BOT_TOKEN", "").strip()
print("="*60)
print("ПРОВЕРКА ТОКЕНА ИЗ .ENV ФАЙЛА")
print("="*60)
print(f"\nТокен из .env: {token}")
if token:
    print(f"Длина токена: {len(token)} символов")
    if ":" in token:
        bot_id = token.split(":")[0]
        print(f"ID бота: {bot_id}")
        print("[OK] Формат токена правильный")
    else:
        print("[WARNING] Формат токена может быть неправильным (должен содержать ':')")
else:
    print("[ERROR] Токен не найден в .env файле!")
print("="*60)
