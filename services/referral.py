from sqlalchemy import select

from database.db import AsyncSessionLocal
from database.models import User

from services.core import (
    add_referral_reward
)


async def process_referral(
    inviter_id: int,
    invited_id: int
):

    if inviter_id == invited_id:
        return False

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(User).where(
                User.user_id == invited_id
            )
        )

        invited_user = result.scalar_one_or_none()

        if not invited_user:
            return False

        if invited_user.referred_by:
            return False

        invited_user.referred_by = inviter_id

        await session.commit()

        return True


async def reward_referrer(
    invited_user_id: int
):

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(User).where(
                User.user_id == invited_user_id
            )
        )

        user = result.scalar_one_or_none()

        if not user:
            return False

        if not user.referred_by:
            return False

        return await add_referral_reward(
            user.referred_by
        )
