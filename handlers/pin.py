from aiogram import Router
from aiogram.types import Message

from services.core import (
    get_user,
    activate_pin
)

from services.referral import (
    reward_referrer
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
async def activate_pin_handler(
    message: Message
):

    pin_code = message.text.strip()

    user = await get_user(
        message.from_user.id
    )

    if not user:

        return await message.answer(
            "❌ User not found."
        )

    success, result = await activate_pin(
        message.from_user.id,
        pin_code
    )

    if not success:

        return await message.answer(
            f"❌ {result}"
        )

    try:

        await reward_referrer(
            message.from_user.id
        )

    except:
        pass

    await message.answer(
        f"""
╔══════════════════╗
🎉 PIN ACTIVATED
╚══════════════════╝

💎 Plan:
{result.upper()}

✅ Premium Access Enabled

🚀 Enjoy Premium Features
"""
    )
