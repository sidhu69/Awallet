import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database.db import init_db

# =========================
# ROUTERS
# =========================
from handlers.start import router as start_router
from handlers.menu import router as menu_router
from handlers.referral import router as referral_router   # ✅ REQUIRED
from handlers.buy_orders import router as buy_orders_router
from handlers.admin import router as admin_router


# =========================
# MAIN FUNCTION
# =========================
async def main():
    # ✅ INIT DB FIRST (CRITICAL)
    init_db()

    # 🤖 Create bot
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    # 🧠 FSM storage
    dp = Dispatcher(storage=MemoryStorage())

    # 📌 REGISTER ROUTERS (ORDER MATTERS)
    dp.include_router(start_router)
    dp.include_router(menu_router)
    dp.include_router(referral_router)   # ✅ THIS WAS MISSING
    dp.include_router(buy_orders_router)
    dp.include_router(admin_router)

    # 🚀 Start polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
