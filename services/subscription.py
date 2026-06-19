from datetime import datetime
from datetime import timedelta

from sqlalchemy import select

from database.db import AsyncSessionLocal
from database.models import User
from database.models import Pin


async def activate_plan(
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
