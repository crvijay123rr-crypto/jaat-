import asyncio

from database.db import engine
from database.models import Base


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(
            Base.metadata.create_all
        )

asyncio.run(create_tables())
