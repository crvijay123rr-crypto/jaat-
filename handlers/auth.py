from aiogram import Router
from aiogram.types import Message

router = Router()


@router.message(
    lambda m: m.text == "🎁 Trial"
)
async def activate_trial(
    message: Message
):

    await message.answer(
        "✅ Trial Activated"
    )
