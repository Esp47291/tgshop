"""Тест функции проверки админа"""
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import config
from handlers.admin import is_admin

print("="*60)
print("ТЕСТ ФУНКЦИИ is_admin")
print("="*60)

print(f"\nADMIN_IDS из config: {config.ADMIN_IDS}")
print(f"Тип ADMIN_IDS: {type(config.ADMIN_IDS)}")
print(f"Типы элементов: {[type(x) for x in config.ADMIN_IDS]}")

test_id = 5324231382
print(f"\nТестируем ID: {test_id}")
print(f"Тип ID: {type(test_id)}")

result = is_admin(test_id)
print(f"\nРезультат is_admin({test_id}): {result}")

if result:
    print("✅ Функция работает правильно!")
else:
    print("❌ Функция не работает!")
    print(f"Проверка вручную: {test_id in config.ADMIN_IDS}")
    print(f"Проверка с int: {int(test_id) in [int(x) for x in config.ADMIN_IDS]}")

print("="*60)
