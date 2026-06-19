from aiogram import Router
from aiogram.types import Message

from database.queries import (
    get_user,
    get_pin
)

router = Router()


@router.message(
    lambda m: m.text == "🔑 Activate PIN"
)
async def ask_pin(message: Message):

    await message.answer(
        """
🔑 PIN ACTIVATION

Please send your PIN code.

Example:

GOLD-ABC123
"""
    )


@router.message()
async def activate_pin(message: Message):

    pin_code = message.text.strip()

    pin = await get_pin(pin_code)

    if not pin:
        return

    user = await get_user(
        message.from_user.id
    )

    if not user:
        return await message.answer(
            "❌ User not found."
        )

    await message.answer(
        f"""
🎉 PIN ACTIVATED

💎 Plan:
{pin.plan.upper()}

📅 Validity:
{pin.days} Days

📂 Files:
{pin.file_limit}

🚀 Premium Access Granted
"""
    )
