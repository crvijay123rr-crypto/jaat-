from datetime import datetime

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True)

    full_name: Mapped[str]

    username: Mapped[str | None]

    plan: Mapped[str] = mapped_column(default="none")

    file_limit: Mapped[int] = mapped_column(default=0)

    files_used: Mapped[int] = mapped_column(default=0)

    banned: Mapped[bool] = mapped_column(default=False)

    expiry_date: Mapped[datetime | None]
