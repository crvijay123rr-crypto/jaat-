import asyncio
import logging

from aiogram import Bot
from aiogram import Dispatcher

from config import BOT_TOKEN

# Routers
from handlers.start import router as start_router
from handlers.auth import router as auth_router
from handlers.profile import router as profile_router
from handlers.admin import router as admin_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

bot = Bot(BOT_TOKEN)

dp = Dispatcher()


async def main():

    # Include Routers
    dp.include_router(start_router)
    dp.include_router(auth_router)
    dp.include_router(profile_router)
    dp.include_router(admin_router)

    print("🚀 Premium Bot Started Successfully")
    print("✅ Start Router Loaded")
    print("✅ Auth Router Loaded")
    print("✅ Profile Router Loaded")
    print("✅ Admin Router Loaded")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
