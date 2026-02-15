import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database.db import init_db

# Routers
from handlers.start import router as start_router
from handlers.menu import router as menu_router
from handlers.buy_orders import router as buy_orders_router
from handlers.admin import router as admin_router


# =========================
# MAIN FUNCTION
# =========================
async def main():
    # ✅ Initialize database FIRST
    init_db()

    # 🤖 Create bot
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    # 🧠 FSM storage
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # 📌 Register routers (ORDER MATTERS)
    dp.include_router(start_router)
    dp.include_router(menu_router)
    dp.include_router(buy_orders_router)
    dp.include_router(admin_router)

    # 🚀 Start polling
    await dp.start_polling(bot)


# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":
    asyncio.run(main())
