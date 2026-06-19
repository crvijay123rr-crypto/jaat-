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

    username: Mapped[str | None] = mapped_column(nullable=True)

    plan: Mapped[str] = mapped_column(
        default="none"
    )

    file_limit: Mapped[int] = mapped_column(
        default=0
    )

    files_used: Mapped[int] = mapped_column(
        default=0
    )

    referral_count: Mapped[int] = mapped_column(
        default=0
    )

    referred_by: Mapped[int | None] = mapped_column(
        nullable=True
    )

    banned: Mapped[bool] = mapped_column(
        default=False
    )

    expiry_date: Mapped[datetime | None] = mapped_column(
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow
    )


class Pin(Base):
    __tablename__ = "pins"

    pin: Mapped[str] = mapped_column(
        primary_key=True
    )

    plan: Mapped[str]

    days: Mapped[int]

    file_limit: Mapped[int]

    max_uses: Mapped[int]

    current_uses: Mapped[int] = mapped_column(
        default=0
    )

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow
    )


class Referral(Base):
    __tablename__ = "referrals"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    inviter_id: Mapped[int]

    invited_id: Mapped[int]

    reward_days: Mapped[int] = mapped_column(
        default=1
    )

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow
    )
