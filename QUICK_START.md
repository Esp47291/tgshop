# ⚡ Быстрый старт

## 🔑 Шаг 1: Получите токен бота

1. Откройте [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте `/newbot`
3. Следуйте инструкциям и получите токен
4. Токен выглядит так: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

## 👤 Шаг 2: Получите ваш ID

1. Откройте [@userinfobot](https://t.me/userinfobot) в Telegram
2. Отправьте `/start`
3. Скопируйте ваш ID (число, например: `123456789`)

## ⚙️ Шаг 3: Настройте .env файл

Откройте файл `.env` и замените:

```env
BOT_TOKEN=ваш_токен_от_BotFather
ADMIN_IDS=ваш_id_от_userinfobot
```

**Пример:**
```env
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
ADMIN_IDS=123456789
```

## 🚀 Шаг 4: Запустите бота

```bash
pip install -r requirements.txt
python main.py
```

## ✅ Готово!

Найдите вашего бота в Telegram и отправьте `/start`

---

**Важно:** 
- Не публикуйте файл `.env` в интернете!
- Храните токены в секрете!
