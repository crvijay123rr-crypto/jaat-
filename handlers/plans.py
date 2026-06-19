from aiogram import Router
from aiogram.types import Message

router = Router()


@router.message(lambda m: m.text == "💎 Plans")
async def plans_cmd(message: Message):

    text = """
╔══════════════════╗
💎 PREMIUM PLANS
╚══════════════════╝

🥈 SILVER
📅 7 Days
📂 100 Files

🥇 GOLD
📅 30 Days
📂 500 Files

💎 PLATINUM
📅 90 Days
♾ Unlimited Files

🎁 Trial
📅 1 Day
📂 10 Files

━━━━━━━━━━━━━━

🔑 Activate a PIN to upgrade.
"""

    await message.answer(text)
