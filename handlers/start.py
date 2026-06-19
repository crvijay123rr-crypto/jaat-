from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.filters.command import CommandObject
from aiogram.types import Message

from keyboards.reply import main_menu

from database.queries import (
    get_user,
    create_user
)

from services.referral import (
    process_referral
)

router = Router()


@router.message(CommandStart())
async def start_cmd(
    message: Message,
    command: CommandObject
):

    user = await get_user(
        message.from_user.id
    )

    is_new_user = False

    if not user:

        is_new_user = True

        await create_user(
            user_id=message.from_user.id,
            full_name=message.from_user.full_name,
            username=message.from_user.username
        )

    # Referral Processing
    if is_new_user and command.args:

        try:

            inviter_id = int(
                command.args
            )

            await process_referral(
                inviter_id,
                message.from_user.id
            )

        except Exception:
            pass

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

👤 Auto Registration
🔒 Secure Database
⚡ Fast Processing
💎 Premium Experience

━━━━━━━━━━━━━━

👇 Choose an option below
"""

    await message.answer(
        text,
        reply_markup=main_menu()
    )
