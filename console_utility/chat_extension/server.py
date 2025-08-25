import asyncio
import logging
from datetime import datetime
from typing import List
from pathlib import Path
import sys

from aiofile import AIOFile, Writer
import names
import websockets
from websockets import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedOK

from api import PrivateBankAPI, PrivateBankAPIError
from services import ExchangeService
from utils import format_date  # для форматирования даты

logging.basicConfig(level=logging.INFO)
LOG_FILE = 'exchange_commands.log'
sys.path.append(str(Path(__file__).resolve().parents[1]))  # чтобы найти api и services

async def log_command(command: str):
    async with AIOFile(LOG_FILE, "a") as afp:
        writer = Writer(afp)
        timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        await writer(f"{timestamp} - {command}\n")
        await afp.fsync()

async def get_exchange(days: int = 1, currencies: List[str] = ["USD", "EUR"]) -> str:
    api = PrivateBankAPI()
    service = ExchangeService(api)
    try:
        rates = await service.get_n_days_rates(days, currencies)
    except PrivateBankAPIError as e:
        return f"Помилка при отриманні курсів: {e}"

    lines = []
    for day in rates:
        for date, values in day.items():
            lines.append(f"Дата: {date}")
            if "error" in values:
                lines.append(f"  Помилка: {values['error']}")
            else:
                for cur, cur_vals in values.items():
                    lines.append(f"  {cur}: Купівля {cur_vals['purchase']}, Продаж {cur_vals['sale']}")
    return "\n".join(lines)

class Server:
    clients = set()

    async def register(self, ws: WebSocketServerProtocol):
        ws.name = names.get_full_name()
        self.clients.add(ws)
        logging.info(f'{ws.remote_address} connects')

    async def unregister(self, ws: WebSocketServerProtocol):
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnects')

    async def send_to_clients(self, message: str):
        if self.clients:
            [await client.send(message) for client in self.clients]

    async def ws_handler(self, ws: WebSocketServerProtocol):
        await self.register(ws)
        try:
            await self.distribute(ws)
        except ConnectionClosedOK:
            pass
        finally:
            await self.unregister(ws)

    async def distribute(self, ws: WebSocketServerProtocol):
        async for message in ws:
            if message.startswith("exchange"):
                parts = message.split()
                days = 1
                if len(parts) > 1 and parts[1].isdigit():
                    days = min(max(int(parts[1]), 1), 10)
                response = await get_exchange(days)
                await log_command(f"exchange {days} від {ws.name}")
                await self.send_to_clients(response)
            else:
                await self.send_to_clients(f"{ws.name}: {message}")

async def main():
    server = Server()
    async with websockets.serve(server.ws_handler, 'localhost', 8080):
        await asyncio.Future()

if __name__ == '__main__':
    asyncio.run(main())
