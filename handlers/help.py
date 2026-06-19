from aiogram import Router
from aiogram.types import Message

router = Router()


@router.message(lambda m: m.text == "ℹ️ Help")
async def help_cmd(message: Message):

    await message.answer(
        """
ℹ️ HELP

👤 Profile
View account details

🎁 Trial
Activate free trial

🔑 Activate PIN
Upgrade your plan

📂 Process File
Upload files

🎯 Referral
Invite friends

📞 Support
Contact admin
"""
    )
