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
            "❌ User not found.\n/start command use karo."
        )

    expiry = (
        user.expiry_date.strftime("%d-%m-%Y %H:%M")
        if user.expiry_date
        else "Not Activated"
    )

    status = (
        "🚫 Banned"
        if user.banned
        else "✅ Active"
    )

    referrals = getattr(
        user,
        "referral_count",
        0
    )

    text = f"""
╔══════════════════╗
👤 USER PROFILE
╚══════════════════╝

🆔 ID:
{user.user_id}

👤 Name:
{user.full_name}

💎 Plan:
{user.plan.upper()}

📂 Usage:
{user.files_used}/{user.file_limit}

📅 Expiry:
{expiry}

🎯 Referrals:
{referrals}

📊 Status:
{status}
"""

    await message.answer(text)
