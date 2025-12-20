def format_order_text(order_data: dict) -> str:
    return f"""
    🛒 *Детали заказа*

    ID: {order_data.get('order_id', 'N/A')}
    Товар: {order_data.get('product', 'Venmo Accounts')}
    Количество: {order_data.get('quantity', 1)} шт
    Сумма: {order_data.get('amount', 0)}$
    Статус: {order_data.get('status', 'pending')}
    """


def format_user_text(user: dict) -> str:
    return f"""
    👤 *Информация о пользователе*

    ID: {user.get('id', 'N/A')}
    Username: @{user.get('username', 'нет')}
    Имя: {user.get('full_name', 'не указано')}
    Баланс: {user.get('balance', 0)}$
    Потратил: {user.get('total_spent', 0)}$
    Зарегистрирован: {user.get('created_at', 'неизвестно')}
    """


def format_payment_text(payment: dict) -> str:
    return f"""
    💸 *Детали платежа*

    ID платежа: {payment.get('id', 'N/A')}
    Сумма: {payment.get('amount', 0)}$
    Сеть: {payment.get('crypto_network', 'не указана')}
    Статус: {payment.get('status', 'pending')}
    Хэш: {payment.get('transaction_hash', 'не указан')}
    """