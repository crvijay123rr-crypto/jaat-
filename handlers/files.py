from aiogram import Router
from aiogram.types import Message

router = Router()


@router.message(
    lambda m: m.text == "📂 Process File"
)
async def process_file(message: Message):

    await message.answer(
        """
📂 FILE PROCESSING

Send a file to start processing.

Supported:

✅ ZIP
✅ PDF
✅ DOCX
✅ HTML
✅ WS
"""
    )
