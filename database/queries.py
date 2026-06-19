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
            username=username
        )

        session.add(user)

        await session.commit()

        return user
