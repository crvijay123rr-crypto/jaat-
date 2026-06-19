from aiogram import Router
from aiogram.types import Message

from database.queries import (
    get_user,
    activate_trial
)

from services.referral import (
    reward_referrer
)

router = Router()


@router.message(lambda m: m.text == "🎁 Trial")
async def activate_trial_btn(message: Message):

    user = await get_user(
        message.from_user.id
    )

    if not user:
        return await message.answer(
            "❌ User not found.\n/start command use karo."
        )

    success = await activate_trial(
        message.from_user.id
    )

    if not success:
        return await message.answer(
            """
⚠️ Trial Already Used

Aap pehle se kisi plan par ho.

👤 Profile check karo.
"""
        )

    # Referral Reward
    try:
        await reward_referrer(
            message.from_user.id
        )
    except:
        pass

    await message.answer(
        """
╔══════════════════╗
🎉 TRIAL ACTIVATED
╚══════════════════╝

💎 Plan:
TRIAL

📅 Validity:
1 Day

📂 File Limit:
10 Files

🎁 Referral Reward:
Enabled

🚀 Premium Features Unlocked
"""
    )
