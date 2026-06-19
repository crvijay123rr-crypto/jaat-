from aiogram import Router
from aiogram.types import Message

router = Router()


@router.message(lambda m: m.text == "🎯 Referral")
async def referral_cmd(message: Message):

    bot_username = "YOUR_BOT_USERNAME"

    link = (
        f"https://t.me/{bot_username}"
        f"?start={message.from_user.id}"
    )

    text = f"""
╔══════════════════╗
🎯 REFERRAL SYSTEM
╚══════════════════╝

🔗 Your Link:

{link}

🎁 Reward:
+1 Day Validity

👥 Share with friends and earn rewards.
"""

    await message.answer(text)
