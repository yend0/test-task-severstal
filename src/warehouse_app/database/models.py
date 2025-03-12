import datetime

from sqlalchemy import DateTime, Numeric
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class BaseORM(DeclarativeBase):
    pass


class RollORM(BaseORM):
    __tablename__ = "roll"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement="auto")
    length: Mapped[float] = mapped_column(Numeric, nullable=False)
    weight: Mapped[float] = mapped_column(Numeric, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    removed_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=True)
