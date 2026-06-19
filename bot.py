import asyncio

from aiogram import Bot
from aiogram import Dispatcher

from config import BOT_TOKEN

bot = Bot(BOT_TOKEN)

dp = Dispatcher()


async def main():

    from handlers.start import router

    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
