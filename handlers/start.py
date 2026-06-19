from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards.reply import main_menu

from database.queries import (
    get_user,
    create_user
)

router = Router()


@router.message(CommandStart())
async def start_cmd(message: Message):

    user = await get_user(
        message.from_user.id
    )

    if not user:

        await create_user(
            user_id=message.from_user.id,
            full_name=message.from_user.full_name,
            username=message.from_user.username
        )

    text = f"""
╔════════════════════╗
🚀 PREMIUM FILE BOT
╚════════════════════╝

👋 Welcome,
{message.from_user.first_name}

✨ Features

🎁 1 Day Free Trial
🔑 Premium PIN System
📂 File Processing
🎯 Referral Rewards
💎 Premium Plans

━━━━━━━━━━━━━━

🎁 Trial Reward
➜ 10 Files

🎯 Referral Reward
➜ +1 Day Validity

━━━━━━━━━━━━━━

👇 Choose an option below
"""

    await message.answer(
        text,
        reply_markup=main_menu()
    )
