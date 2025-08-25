from datetime import datetime, timedelta
from typing import List, Dict, Optional
from api import PrivateBankAPI, PrivateBankAPIError
import aiohttp

class ExchangeService: # Сервіс для обробки курсів валют за останні дні
    def __init__(self, api: PrivateBankAPI):
        self.api = api

    # Курс валют за останні дні, Кожен словник буде курс за один день
    async def get_n_days_rates(self, days: int, currencies: List[str]) -> List[Dict[str, Dict[str, Optional[float]]]]:
        if days > 10:
            raise ValueError('Не більше 10 днів')

        result: List[Dict[str, Dict[str, Optional[float]]]] = []

        async with aiohttp.ClientSession(timeout=self.api._timeout) as session: # Асинхронна сесія
            for i in range(days):
                date_obj = datetime.now() - timedelta(days=i)
                date_str = date_obj.strftime('%d.%m.%Y')

                try:
                    raw_data = await self.api.fetch_day_raw(session, date_str)  # Тільки потрібні валюти
                    day_rates = self.api.extract_rates_for(raw_data, currencies)  # Додаємо у результати у форматі
                    result.append({date_str: day_rates})
                except PrivateBankAPIError as e:
                    result.append({date_str: {"error": str(e)}})  # Якщо була помилка

            return result


