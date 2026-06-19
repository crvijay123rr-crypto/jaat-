from datetime import datetime
from datetime import timedelta

from sqlalchemy import select

from database.db import AsyncSessionLocal
from database.models import User
from database.models import Pin


# =========================
# USER
# =========================

async def get_user(user_id: int):

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(User).where(
                User.user_id == user_id
            )
        )

        return result.scalar_one_or_none()


# =========================
# TRIAL
# =========================

async def activate_trial(
    user_id: int
):

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(User).where(
                User.user_id == user_id
            )
        )

        user = result.scalar_one_or_none()

        if not user:
            return False

        if user.plan != "none":
            return False

        user.plan = "trial"

        user.file_limit = 10

        user.files_used = 0

        user.expiry_date = (
            datetime.utcnow()
            + timedelta(days=1)
        )

        await session.commit()

        return True


# =========================
# PIN
# =========================

async def activate_pin(
    user_id: int,
    pin_code: str
):

    async with AsyncSessionLocal() as session:

        pin_result = await session.execute(
            select(Pin).where(
                Pin.pin == pin_code
            )
        )

        pin = pin_result.scalar_one_or_none()

        if not pin:
            return False, "Invalid PIN"

        if pin.current_uses >= pin.max_uses:
            return False, "PIN Expired"

        user_result = await session.execute(
            select(User).where(
                User.user_id == user_id
            )
        )

        user = user_result.scalar_one_or_none()

        if not user:
            return False, "User Not Found"

        user.plan = pin.plan

        user.file_limit = pin.file_limit

        user.files_used = 0

        user.expiry_date = (
            datetime.utcnow()
            + timedelta(days=pin.days)
        )

        pin.current_uses += 1

        await session.commit()

        return True, pin.plan


# =========================
# REFERRAL
# =========================

async def add_referral_reward(
    inviter_id: int
):

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(User).where(
                User.user_id == inviter_id
            )
        )

        user = result.scalar_one_or_none()

        if not user:
            return False

        if not user.expiry_date:

            user.expiry_date = (
                datetime.utcnow()
                + timedelta(days=1)
            )

        else:

            user.expiry_date += timedelta(
                days=1
            )

        user.referral_count += 1

        await session.commit()

        return True


# =========================
# BAN
# =========================

async def ban_user(
    user_id: int
):

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(User).where(
                User.user_id == user_id
            )
        )

        user = result.scalar_one_or_none()

        if not user:
            return False

        user.banned = True

        await session.commit()

        return True


async def unban_user(
    user_id: int
):

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(User).where(
                User.user_id == user_id
            )
        )

        user = result.scalar_one_or_none()

        if not user:
            return False

        user.banned = False

        await session.commit()

        return True


# =========================
# CHECKS
# =========================

def is_expired(user):

    if not user.expiry_date:
        return True

    return (
        datetime.utcnow()
        > user.expiry_date
    )


def file_limit_reached(user):

    if user.file_limit == -1:
        return False

    return (
        user.files_used
        >= user.file_limit
    )


# =========================
# FILE USAGE
# =========================

async def add_file_usage(
    user_id: int
):

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(User).where(
                User.user_id == user_id
            )
        )

        user = result.scalar_one_or_none()

        if not user:
            return False

        user.files_used += 1

        await session.commit()

        return True
