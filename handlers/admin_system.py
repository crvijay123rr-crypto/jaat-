import random
import string

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from sqlalchemy import select
from sqlalchemy import func

from config import ADMINS

from database.db import AsyncSessionLocal
from database.models import User
from database.models import Pin

from services.core import (
    ban_user,
    unban_user
)

router = Router()


# ==========================
# ADMIN CHECK
# ==========================

def is_admin(user_id):

    return user_id in ADMINS


# ==========================
# ADMIN PANEL
# ==========================

@router.message(Command("admin"))
async def admin_panel(message: Message):

    if not is_admin(message.from_user.id):
        return

    await message.answer(
        """
🛠 ADMIN PANEL

/stats
/users
/search

/createpin

/ban
/unban

/broadcast
"""
    )


# ==========================
# STATS
# ==========================

@router.message(Command("stats"))
async def stats_cmd(message: Message):

    if not is_admin(message.from_user.id):
        return

    async with AsyncSessionLocal() as session:

        total_users = await session.scalar(
            select(func.count()).select_from(User)
        )

    await message.answer(
        f"""
📊 BOT STATS

👥 Users:
{total_users}
"""
    )


# ==========================
# USERS
# ==========================

@router.message(Command("users"))
async def users_cmd(message: Message):

    if not is_admin(message.from_user.id):
        return

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(User)
        )

        users = result.scalars().all()

    await message.answer(
        f"👥 Total Users: {len(users)}"
    )


# ==========================
# SEARCH USER
# ==========================

@router.message(Command("search"))
async def search_cmd(message: Message):

    if not is_admin(message.from_user.id):
        return

    try:

        user_id = int(
            message.text.split()[1]
        )

    except:

        return await message.answer(
            "Usage:\n/search user_id"
        )

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(User).where(
                User.user_id == user_id
            )
        )

        user = result.scalar_one_or_none()

    if not user:

        return await message.answer(
            "❌ User Not Found"
        )

    await message.answer(
        f"""
👤 USER

🆔 {user.user_id}

💎 {user.plan}

📂 {user.files_used}/{user.file_limit}
"""
    )


# ==========================
# CREATE PIN
# ==========================

@router.message(Command("createpin"))
async def create_pin_cmd(message: Message):

    if not is_admin(message.from_user.id):
        return

    try:

        args = message.text.split()

        plan = args[1]
        days = int(args[2])
        files = int(args[3])
        uses = int(args[4])

    except:

        return await message.answer(
            """
Usage:

/createpin GOLD 30 500 50
"""
        )

    pin_code = ''.join(
        random.choices(
            string.ascii_uppercase +
            string.digits,
            k=10
        )
    )

    async with AsyncSessionLocal() as session:

        pin = Pin(
            pin=pin_code,
            plan=plan,
            days=days,
            file_limit=files,
            max_uses=uses
        )

        session.add(pin)

        await session.commit()

    await message.answer(
        f"""
✅ PIN CREATED

🔑 {pin_code}

💎 {plan}
📅 {days} Days
📂 {files} Files
👥 {uses} Uses
"""
    )


# ==========================
# BAN
# ==========================

@router.message(Command("ban"))
async def ban_cmd(message: Message):

    if not is_admin(message.from_user.id):
        return

    try:

        user_id = int(
            message.text.split()[1]
        )

    except:

        return await message.answer(
            "Usage:\n/ban user_id"
        )

    success = await ban_user(
        user_id
    )

    if success:

        await message.answer(
            "✅ User Banned"
        )

    else:

        await message.answer(
            "❌ User Not Found"
        )


# ==========================
# UNBAN
# ==========================

@router.message(Command("unban"))
async def unban_cmd(message: Message):

    if not is_admin(message.from_user.id):
        return

    try:

        user_id = int(
            message.text.split()[1]
        )

    except:

        return await message.answer(
            "Usage:\n/unban user_id"
        )

    success = await unban_user(
        user_id
    )

    if success:

        await message.answer(
            "✅ User Unbanned"
        )

    else:

        await message.answer(
            "❌ User Not Found"
        )


# ==========================
# BROADCAST
# ==========================

@router.message(Command("broadcast"))
async def broadcast_cmd(message: Message):

    if not is_admin(message.from_user.id):
        return

    text = message.text.replace(
        "/broadcast",
        ""
    ).strip()

    if not text:

        return await message.answer(
            "Usage:\n/broadcast Hello"
        )

    sent = 0

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(User)
        )

        users = result.scalars().all()

    for user in users:

        try:

            await message.bot.send_message(
                user.user_id,
                text
            )

            sent += 1

        except:
            pass

    await message.answer(
        f"✅ Sent To {sent} Users"
  )
