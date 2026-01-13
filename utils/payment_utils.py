"""
Утилиты для работы с платежными системами
Интеграция с CryptoBot API и проверка криптоплатежей
"""
import aiohttp
import logging
from typing import Optional, Dict, Any
import config

logger = logging.getLogger(__name__)


class CryptoBotAPI:
    """Класс для работы с CryptoBot API"""
    
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://pay.crypt.bot/api"
        self.headers = {
            "Crypto-Pay-API-Token": token
        }
    
    async def create_invoice(
        self,
        amount: float,
        currency: str = "USD",
        description: str = "",
        paid_btn_name: str = "callback",
        paid_btn_url: str = "",
        payload: str = ""
    ) -> Optional[Dict[str, Any]]:
        """Создание инвойса в CryptoBot"""
        try:
            url = f"{self.base_url}/createInvoice"
            params = {
                "asset": "USDT",
                "amount": str(amount),
                "description": description,
                "paid_btn_name": paid_btn_name,
                "paid_btn_url": paid_btn_url,
                "payload": payload
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("ok"):
                            logger.info(f"Invoice created: {data.get('result', {}).get('invoice_id')}")
                            return data.get("result")
                    else:
                        error_text = await response.text()
                        logger.error(f"CryptoBot API error: {error_text}")
                        return None
        except Exception as e:
            logger.error(f"Error creating invoice: {e}")
            return None
    
    async def get_invoice_status(self, invoice_id: int) -> Optional[Dict[str, Any]]:
        """Проверка статуса инвойса"""
        try:
            url = f"{self.base_url}/getInvoices"
            params = {"invoice_ids": str(invoice_id)}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("ok") and data.get("result", {}).get("items"):
                            return data.get("result", {}).get("items")[0]
                    return None
        except Exception as e:
            logger.error(f"Error checking invoice status: {e}")
            return None
    
    async def get_me(self) -> Optional[Dict[str, Any]]:
        """Проверка подключения к API"""
        try:
            url = f"{self.base_url}/getMe"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("result") if data.get("ok") else None
        except Exception as e:
            logger.error(f"Error checking CryptoBot connection: {e}")
            return None


class CryptoPaymentChecker:
    """Класс для проверки криптоплатежей"""
    
    def __init__(self):
        self.networks = {
            "trc20": {
                "name": "USDT (TRC20)",
                "explorer": "https://tronscan.org/#/transaction/",
                "api": "https://api.trongrid.io/v1/accounts/"
            },
            "bep20": {
                "name": "USDT (BEP20)",
                "explorer": "https://bscscan.com/tx/",
                "api": "https://api.bscscan.com/api"
            },
            "ton": {
                "name": "TON",
                "explorer": "https://tonscan.org/tx/",
                "api": "https://toncenter.com/api/v2/"
            },
            "eth": {
                "name": "ETH",
                "explorer": "https://etherscan.io/tx/",
                "api": "https://api.etherscan.io/api"
            }
        }
    
    async def verify_transaction(
        self,
        network: str,
        wallet_address: str,
        amount: float,
        transaction_hash: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Проверка транзакции (упрощенная версия)
        В реальном проекте здесь должна быть интеграция с блокчейн-эксплорерами
        """
        result = {
            "verified": False,
            "message": "",
            "transaction_hash": transaction_hash
        }
        
        # В реальном проекте здесь должна быть проверка через API блокчейна
        # Для демонстрации возвращаем заглушку
        # Админ должен вручную проверять платежи через админ-панель
        
        if transaction_hash:
            result["message"] = f"Транзакция получена: {transaction_hash}\nОжидает ручной проверки администратором."
        else:
            result["message"] = "Ожидает проверки администратором."
        
        return result
    
    def get_wallet_info(self, network: str) -> Dict[str, str]:
        """Получение информации о кошельке для сети"""
        wallet_key = f"USDT_{network.upper()}" if network in ["trc20", "bep20"] else network.upper()
        wallet_address = config.WALLETS.get(wallet_key, "")
        
        network_info = self.networks.get(network, {})
        
        return {
            "address": wallet_address,
            "network": network_info.get("name", network),
            "explorer": network_info.get("explorer", "")
        }


# Глобальный экземпляр CryptoBot API
cryptobot_api = None

def get_cryptobot_api() -> Optional[CryptoBotAPI]:
    """Получение экземпляра CryptoBot API"""
    global cryptobot_api
    if not cryptobot_api and config.CRYPTOBOT_TOKEN:
        cryptobot_api = CryptoBotAPI(config.CRYPTOBOT_TOKEN)
    return cryptobot_api
