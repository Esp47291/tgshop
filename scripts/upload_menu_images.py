import asyncio
import os
import sys

from aiogram import Bot
from aiogram.types import FSInputFile

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import config


MEDIA_ITEMS = [
    ("START_MENU_FILE_ID", config.START_MENU_IMAGE),
    ("SUPPORT_MENU_FILE_ID", config.SUPPORT_MENU_IMAGE),
    ("BUY_MENU_FILE_ID", config.BUY_MENU_IMAGE),
    ("PAYMENT_MENU_FILE_ID", config.PAYMENT_MENU_IMAGE),
]


async def main():
    chat_id = sys.argv[1] if len(sys.argv) > 1 else os.getenv("MENU_MEDIA_CHAT_ID", "").strip()
    if not chat_id:
        raise ValueError("Pass chat id as first argument or set MENU_MEDIA_CHAT_ID")

    bot = Bot(token=config.BOT_TOKEN)
    try:
        for env_name, image_path in MEDIA_ITEMS:
            print(f"Uploading {env_name} from {image_path}...")
            message = await bot.send_photo(
                chat_id=chat_id,
                photo=FSInputFile(image_path),
                request_timeout=180
            )
            file_id = message.photo[-1].file_id
            print(f"{env_name}={file_id}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
