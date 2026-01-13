"""Скрипт для обновления ADMIN_IDS в .env"""
import os
import re

ADMIN_ID = "5324231382"

# Читаем файл .env
env_path = ".env"
if not os.path.exists(env_path):
    print(f"Файл {env_path} не найден!")
    exit(1)

with open(env_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Заменяем ADMIN_IDS
old_pattern = r'ADMIN_IDS=.*'
new_line = f'ADMIN_IDS={ADMIN_ID}'

if re.search(old_pattern, content):
    content = re.sub(old_pattern, new_line, content)
    print(f"[OK] ADMIN_IDS обновлен на {ADMIN_ID}")
else:
    # Если строка не найдена, добавляем
    content = f'{content}\n{new_line}\n'
    print(f"[OK] ADMIN_IDS добавлен: {ADMIN_ID}")

# Сохраняем файл
with open(env_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"[OK] Файл {env_path} обновлен успешно!")

# Проверяем результат
from dotenv import load_dotenv
load_dotenv()
admin_ids_str = os.getenv('ADMIN_IDS', '')
if ADMIN_ID in admin_ids_str:
    print(f"[OK] Проверка: ADMIN_IDS правильно загружен: {admin_ids_str}")
else:
    print(f"[ERROR] Ошибка: ADMIN_IDS не загружен правильно. Текущее значение: {admin_ids_str}")
