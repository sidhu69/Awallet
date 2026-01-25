# main.py - Bot entry point
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database import load_db
from states import Registration, BuyOrder  # ← optional, but good to have
from handlers.registration import router as reg_router
from handlers.buy_order import router as buy_router
from handlers.admin_commands import router as admin_router

dp = Dispatcher(storage=MemoryStorage())

dp.include_router(reg_router)
dp.include_router(buy_router)
dp.include_router(admin_router)

async def main():
    logging.basicConfig(level=logging.INFO)
    load_db()
    bot = Bot(token=BOT_TOKEN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
