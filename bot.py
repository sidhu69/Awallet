# Line 1
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

# Line 8
from config import BOT_TOKEN
from database.db import init_db

# Line 11 - Routers
from handlers.start import router as start_router
from handlers.menu import router as menu_router
from handlers.buy_orders import router as buy_orders_router
from handlers.admin import router as admin_router
from handlers.referral import router as referral_router


# =========================
# MAIN FUNCTION
# =========================
# Line 19
async def main():
    # Line 21
    # ✅ Initialize database FIRST
    init_db()

    # Line 24
    # 🤖 Create bot
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    # Line 30
    # 🧠 FSM storage
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Line 34
    # 📌 Register routers (ORDER MATTERS)
    dp.include_router(start_router)
    dp.include_router(menu_router)
    dp.include_router(buy_orders_router)
    dp.include_router(admin_router)
    dp.include_router(referral_router)

    # Line 40
    # 🚀 Start polling
    await dp.start_polling(bot)


# Line 44
if __name__ == "__main__":
    asyncio.run(main())
