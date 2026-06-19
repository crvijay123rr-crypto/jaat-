from aiogram import Router
from aiogram.types import Message

from database.queries import get_user

router = Router()


@router.message(lambda m: m.text == "👤 Profile")
async def profile_cmd(message: Message):

    user = await get_user(
        message.from_user.id
    )

    if not user:
        return await message.answer(
            "❌ User not found"
        )

    text = f"""
👤 PROFILE

🆔 {user.user_id}

💎 Plan : {user.plan}

📂 Used : {user.files_used}/{user.file_limit}

🚫 Banned : {user.banned}
"""

    await message.answer(text)
