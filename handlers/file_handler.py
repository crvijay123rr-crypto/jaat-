from aiogram import Router
from aiogram.types import Message

from services.core import (
    get_user,
    is_expired,
    file_limit_reached,
    add_file_usage
)

router = Router()


SUPPORTED_FILES = [
    ".zip",
    ".pdf",
    ".docx",
    ".html",
    ".ws"
]


@router.message(lambda m: m.document)
async def process_document(message: Message):

    user = await get_user(
        message.from_user.id
    )

    if not user:
        return await message.answer(
            "❌ User not found.\nUse /start first."
        )

    if user.banned:
        return await message.answer(
            "🚫 Your account is banned."
        )

    if is_expired(user):
        return await message.answer(
            """
⏳ Subscription Expired

Activate Trial or PIN.
"""
        )

    if file_limit_reached(user):
        return await message.answer(
            """
📂 File Limit Reached

Upgrade your plan.
"""
        )

    document = message.document

    filename = (
        document.file_name or ""
    ).lower()

    if not any(
        filename.endswith(ext)
        for ext in SUPPORTED_FILES
    ):
        return await message.answer(
            """
❌ Unsupported File

Allowed:

ZIP
PDF
DOCX
HTML
WS
"""
        )

    await add_file_usage(
        message.from_user.id
    )

    await message.answer(
        f"""
✅ File Accepted

📄 Name:
{document.file_name}

📦 Size:
{round(document.file_size / 1024, 2)} KB

🚀 Processing Started...
"""
    )

    # Future Processing Logic Here

    await message.answer(
        """
🎉 Processing Complete

Result Ready.
"""
    )
