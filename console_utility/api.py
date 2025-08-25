# API работа з ПриватБанком
import aiohttp
from typing import Any, Dict, Optional

API_URL = "https://api.privatbank.ua/p24api/exchange_rates?json&date={date}"

class PrivateBankAPIError(Exception): # Клас помилок для API ПриватБанку
    pass

class PrivateBankAPI: # Взаємодія з ПриватБанку, методи для отримання даних для обробки
    def __init__(self, timeout_seconds: float = 15.0): # Таймаут у секундах для запитів
        self._timeout = aiohttp.ClientTimeout(total=timeout_seconds)


    async def fetch_day_raw(self, session: aiohttp.ClientSession, date_str: str) -> Dict[str, Any]:
        url = API_URL.format(date=date_str)
        try:
            async with session.get(url) as response: # Асихронний запит Гет
                if response.status != 200: # Якщо статус не != 200 Помилка
                    text = await response.text()
                    raise PrivateBankAPIError(f"HTTP {response.status}: {text[:200]}")
                return await response.json()
        except (aiohttp.ClientError, aiohttp.ServerTimeoutError) as e: # Помилки
            raise PrivateBankAPIError(f"Network error: {e}") from e


    def extract_rates_for(self, raw: Dict[str, Any], currencies: list[str]) -> Dict[str, Dict[str, Optional[float]]]:
        result: Dict[str, Dict[str, Optional[float]]] = {}
        for item in raw.get("exchangeRate", []): # Курси з Json
            code = item.get("currency") # Код валюти
            if code in currencies:
                sale = item.get("saleRate") # Курс продажу ПриватБанку
                purchase = item.get("purchaseRate") # Курс купівлі ПриватБанку
                if sale is None or purchase is None: # Якщо курсів немає
                    sale = item.get("saleRateNB")
                    purchase = item.get("purchaseRateNB")
                if sale is not None and purchase is not None:
                    result[code] = {"sale": float(sale), "purchase": float(purchase)} # Додаємо результати у словник з float
        return result



