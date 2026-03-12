Use these files for bot menu images:

- `data/images/start_menu.png`
- `data/images/support_menu.png`
- `data/images/buy_menu.png`
- `data/images/payment_menu.png`

Optional `.env` variables for stable Telegram reuse via `file_id`:

- `START_MENU_FILE_ID=`
- `SUPPORT_MENU_FILE_ID=`
- `BUY_MENU_FILE_ID=`
- `PAYMENT_MENU_FILE_ID=`

If a `*_FILE_ID` variable is empty, the bot falls back to the local file from `data/images`.
