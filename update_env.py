"""Скрипт для обновления .env файла"""
import os
import re
import sys

# Исправление кодировки для Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Токен бота
BOT_TOKEN = "8513744371:AAES-lLCYCuHuQKUjCtdpIRcAiHuWkTTJpg"

# Читаем файл .env
env_path = ".env"
if not os.path.exists(env_path):
    print(f"[ERROR] Файл {env_path} не найден!")
    exit(1)

with open(env_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Заменяем BOT_TOKEN
old_pattern = r'BOT_TOKEN=.*'
new_line = f'BOT_TOKEN={BOT_TOKEN}'

if re.search(old_pattern, content):
    content = re.sub(old_pattern, new_line, content)
    print("[OK] BOT_TOKEN обновлен")
else:
    # Если строка не найдена, добавляем в начало
    content = f'{new_line}\n{content}'
    print("[OK] BOT_TOKEN добавлен")

# Сохраняем файл
with open(env_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"[OK] Файл {env_path} обновлен успешно!")

# Проверяем результат
from dotenv import load_dotenv
load_dotenv()
token = os.getenv('BOT_TOKEN', '')
if token == BOT_TOKEN:
    print(f"[OK] Проверка: токен правильно загружен ({token[:20]}...)")
else:
    print(f"[ERROR] Ошибка: токен не загружен правильно. Текущее значение: {token[:20] if token else 'ПУСТО'}")
