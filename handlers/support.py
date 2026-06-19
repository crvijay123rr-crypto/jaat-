from aiogram import Router
from aiogram.types import Message

router = Router()


@router.message(lambda m: m.text == "📞 Support")
async def support_cmd(message: Message):

    await message.answer(
        """
📞 SUPPORT

Need help?

Contact Admin:
@course_hub2bot

Response Time:
24 Hours
"""
    )
