import asyncio
import logging

from database.db import engine
from database.models import Base


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


async def create_tables():

    try:

        async with engine.begin() as conn:

            await conn.run_sync(
                Base.metadata.create_all
            )

        logging.info(
            "✅ Database Tables Created Successfully"
        )

    except Exception as e:

        logging.error(
            f"❌ Database Error: {e}"
        )


if __name__ == "__main__":

    asyncio.run(
        create_tables()
    )
