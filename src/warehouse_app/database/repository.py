import abc
import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from warehouse_app.api.schemas import RollRequestCreate
from warehouse_app.database.models import BaseORM, RollORM

T = TypeVar("T", bound=BaseORM)
S = TypeVar("S", bound=BaseModel)


class AbstractRepository(Generic[T, S], abc.ABC):
    @abc.abstractmethod
    async def get_by_id(self, model_id: int) -> T | None:
        raise NotImplementedError()

    @abc.abstractmethod
    async def get_all(self, filters: dict[str, Any] | None = None) -> list[T]:
        raise NotImplementedError()

    @abc.abstractmethod
    async def add(self, model: S) -> T:
        raise NotImplementedError()


class SqlAlchemyRepository(AbstractRepository[T, S]):
    def __init__(self, session: AsyncSession, orm_model: type[T], pydantic_model: type[S]):
        self._session = session
        self._orm_model = orm_model
        self._pydantic_model = pydantic_model

    async def get_by_id(self, model_id: int) -> T | None:
        stmt = select(self._orm_model).where(self._orm_model.id == model_id)
        result = await self._session.execute(stmt)
        orm_instance = result.scalar_one_or_none()
        if orm_instance:
            return orm_instance
        return None

    async def get_all(self, filters: dict[str, Any] | None = None) -> list[T]:
        stmt = select(self._orm_model).order_by(self._orm_model.id)

        if filters:
            criterias = []

            for attr, value in filters.items():
                column = getattr(self._orm_model, attr, None)

                if column is None:
                    continue
                elif isinstance(value, list) and len(value) == 2:
                    criterias.append(column.between(value[0], value[1]))

            if criterias:
                stmt = stmt.where(and_(*criterias))

        result = await self._session.execute(stmt)
        orm_instances = result.scalars().all()
        return orm_instances

    async def add(self, model: S) -> T:
        orm_instance = self._orm_model(**model.model_dump())
        self._session.add(orm_instance)
        await self._session.flush()
        await self._session.refresh(orm_instance)
        await self._session.commit()
        return orm_instance


class RollAbstractReposity(SqlAlchemyRepository[RollORM, RollRequestCreate], abc.ABC):
    @abc.abstractmethod
    async def delete(self, model_id: int) -> RollORM | None:
        raise NotImplementedError()

    @abc.abstractmethod
    async def get_rolls_in_stock_during_period(
        self, date_range: dict[str, list[datetime.datetime]]
    ) -> list[RollORM] | None:
        raise NotImplementedError()


class RollReposity(RollAbstractReposity):
    async def delete(self, model_id: int) -> RollORM | None:
        orm_instance = await self.get_by_id(model_id)
        if orm_instance:
            if orm_instance.removed_at:
                return None
            orm_instance.removed_at = datetime.datetime.now(datetime.UTC)
            self._session.add(orm_instance)
            await self._session.commit()
            return orm_instance
        return None

    async def get_rolls_in_stock_during_period(
        self, date_range: dict[str, list[datetime.datetime]]
    ) -> list[RollORM] | None:
        stmt = select(self._orm_model)

        start_date, end_date = date_range["date_range"]

        stmt = stmt.filter(
            or_(
                and_(self._orm_model.created_at >= start_date, self._orm_model.created_at <= end_date),
                and_(
                    self._orm_model.removed_at is not None,
                    self._orm_model.removed_at >= start_date,
                    self._orm_model.removed_at <= end_date,
                ),
                and_(
                    self._orm_model.created_at < start_date,
                    or_(self._orm_model.removed_at is None, self._orm_model.removed_at > end_date),
                ),
            )
        )

        result = await self._session.execute(stmt)
        rolls = result.scalars().all()
        return rolls if rolls else None
