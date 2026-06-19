from datetime import datetime, timedelta

from sqlalchemy import select

from database.db import AsyncSessionLocal
from database.models import User


async def get_user(user_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.user_id == user_id)
        )
        return result.scalar_one_or_none()


async def create_user(
    user_id,
    full_name,
    username
):
    async with AsyncSessionLocal() as session:

        user = User(
            user_id=user_id,
            full_name=full_name,
            username=username,
            plan="none",
            file_limit=0,
            files_used=0,
            banned=False
        )

        session.add(user)

        await session.commit()

        return user


async def activate_trial(user_id: int):

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(User).where(User.user_id == user_id)
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
            datetime.utcnow() + timedelta(days=1)
        )

        await session.commit()

        return True


async def update_files_used(
    user_id: int,
    count: int = 1
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

        user.files_used += count

        await session.commit()

        return True
