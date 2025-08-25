from datetime import datetime

def format_date(date_object: datetime) -> str: # Перетворення дати у формат
    return date_object.strftime("%d.%m.%Y")

def validate_currenc(currenc: list[str]) -> list[str]: # Перевірка введених валют
    allowed = ["USD", "EUR", "CHF", "GBP", "PLZ", "SEK", "XAU", "CAD"]
    return [c for c in currenc if c in allowed]

def print_rates(rates: list[dict]):
    for day in rates:
        for date, value in day.items():
            print(f"\nДата: {date}")
            if 'error' in value:
                print(f'  Помилка: {value["error"]}')
            else:
                for cur, cur_vals in value.items():
                    print(f'  {cur}: Купівля {cur_vals["purchase"]}, Продаж {cur_vals["sale"]}')


