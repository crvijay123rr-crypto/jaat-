from aiogram import Router
from aiogram.types import Message

from database.queries import get_user

router = Router()


@router.message(lambda m: m.text == "🎁 Trial")
async def activate_trial(message: Message):

    user = await get_user(message.from_user.id)

    if not user:
        return await message.answer(
            "❌ User not found.\n/start command use karo."
        )

    if user.plan != "none":
        return await message.answer(
            "⚠️ Aap pehle hi Trial ya Premium Plan use kar rahe ho."
        )

    await message.answer(
        """
🎉 Trial Activated Successfully

💎 Plan : Trial
📅 Validity : 1 Day
📂 File Limit : 10

🚀 Enjoy Premium Features
"""
    )
