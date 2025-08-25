# Запуск
import sys
import asyncio
from api import PrivateBankAPI
from services import ExchangeService
from utils import print_rates

async def main(): # Перевіряє чи користувач передав кількість днів
    if len(sys.argv) < 2:
        print("Використання: python3 main.py <кількість днів (1-10)>")
        return

    try:
        days = int(sys.argv[1])
    except ValueError:
        print("Помилка: кількість днів має бути цілим числом")
        return

    if not 1 <= days <= 10:
        print("Помилка: кількість днів має бути від 1 до 10")
        return

    currencies = ["USD", "EUR"] # Валюти

    api = PrivateBankAPI()
    service = ExchangeService(api)

    rates = await service.get_n_days_rates(days, currencies) # Курс валют
    print(rates) # Виводимо результат
    print_rates(rates)

if __name__ == "__main__":
    asyncio.run(main())
