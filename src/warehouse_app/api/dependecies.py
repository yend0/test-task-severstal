from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from warehouse_app.api.schemas import RollRequestCreate
from warehouse_app.core.config import Config
from warehouse_app.database import connection, repository
from warehouse_app.database.models import RollORM
from warehouse_app.service import roll as roll_service

database_client: connection.DatabaseClient = connection.database_sqlalchemy_factory(database_config=Config.database)


async def get_roll_repository(
    session: Annotated[AsyncSession, Depends(database_client.async_session_dependency)],
) -> repository.RollAbstractReposity:
    return repository.RollReposity(session=session, orm_model=RollORM, pydantic_model=RollRequestCreate)


async def get_roll_service(
    roll_repo: Annotated[repository.RollAbstractReposity, Depends(get_roll_repository)],
) -> roll_service.RollService:
    return roll_service.RollService(roll_repo=roll_repo)
