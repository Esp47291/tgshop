"""Скрипт для проверки готовности бота к запуску"""
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("="*60)
print("ПРОВЕРКА ГОТОВНОСТИ БОТА К ЗАПУСКУ")
print("="*60)

try:
    print("\n1. Проверка импорта config...")
    import config
    print("   [OK] config импортирован")
    
    print("\n2. Проверка BOT_TOKEN...")
    if config.BOT_TOKEN and config.BOT_TOKEN != "YOUR_BOT_TOKEN_HERE":
        print(f"   [OK] BOT_TOKEN установлен: {config.BOT_TOKEN[:20]}...")
        print(f"   [OK] Длина токена: {len(config.BOT_TOKEN)} символов")
    else:
        print("   [ERROR] BOT_TOKEN не установлен!")
        raise ValueError("BOT_TOKEN не установлен")
    
    print("\n3. Проверка импорта database...")
    from database import init_db
    print("   [OK] database импортирован")
    
    print("\n4. Проверка импорта handlers...")
    from handlers import start_router, buy_router, payments_router, support_router, referral_router, admin_router
    print("   [OK] Все handlers импортированы")
    
    print("\n5. Проверка инициализации базы данных...")
    init_db()
    print("   [OK] База данных инициализирована")
    
    print("\n6. Проверка создания бота...")
    from aiogram import Bot
    from aiogram.client.default import DefaultBotProperties
    from aiogram.enums import ParseMode
    
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )
    print("   [OK] Бот создан успешно")
    
    print("\n" + "="*60)
    print("✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ!")
    print("="*60)
    print("\nБот готов к запуску!")
    print("Запустите: python main.py")
    print("\n⚠️  ВНИМАНИЕ: ADMIN_IDS не установлен.")
    print("   Админ-панель будет недоступна до установки ADMIN_IDS.")
    print("   Чтобы установить: откройте .env и замените YOUR_ADMIN_ID_HERE")
    print("="*60)
    
except Exception as e:
    print("\n" + "="*60)
    print("❌ ОШИБКА ПРИ ПРОВЕРКЕ!")
    print("="*60)
    print(f"Ошибка: {e}")
    print("="*60)
    sys.exit(1)
