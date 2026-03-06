import re

def escape_md(text):
    """Экранирует специальные символы Markdown в тексте"""
    if not isinstance(text, str):
        return text
    return re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', text)

def format_order_text(order_data: dict) -> str:
    return f"""
    🛒 *Детали заказа*

    ID: {escape_md(order_data.get('order_id', 'N/A'))}
    Товар: {escape_md(order_data.get('product', 'Venmo Accounts'))}
    Количество: {order_data.get('quantity', 1)} шт
    Сумма: {order_data.get('amount', 0)}$
    Статус: {escape_md(order_data.get('status', 'pending'))}
    """


def format_user_text(user: dict) -> str:
    return f"""
    👤 *Информация о пользователе*

    ID: {user.get('id', 'N/A')}
    Username: @{escape_md(user.get('username', 'нет'))}
    Имя: {escape_md(user.get('full_name', 'не указано'))}
    Баланс: {user.get('balance', 0)}$
    Потратил: {user.get('total_spent', 0)}$
    Зарегистрирован: {escape_md(str(user.get('created_at', 'неизвестно')))}
    """


def format_payment_text(payment: dict) -> str:
    return f"""
    💸 *Детали платежа*

    ID платежа: {payment.get('id', 'N/A')}
    Сумма: {payment.get('amount', 0)}$
    Сеть: {escape_md(payment.get('crypto_network', 'не указана'))}
    Статус: {escape_md(payment.get('status', 'pending'))}
    Хэш: {escape_md(payment.get('transaction_hash', 'не указан'))}
    """