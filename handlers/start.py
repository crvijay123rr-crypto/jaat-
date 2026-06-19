from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards.reply import main_menu

router = Router()


@router.message(CommandStart())
async def start_cmd(message: Message):

    text = f"""
🚀 Welcome {message.from_user.first_name}

Premium File Processing Bot

🎁 Trial Available
🔑 PIN System
📂 File Processing
🎯 Referral Program
💎 Premium Plans
"""

    await message.answer(
        text,
        reply_markup=main_menu()
    )
