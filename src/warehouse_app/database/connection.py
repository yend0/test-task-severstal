from typing import AsyncGenerator, Any
from warehouse_app.core.config import DatabaseConfig

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)


class DatabaseSQLAlchemy:
    def __init__(self, url: str, echo: bool = False) -> None:
        
        self._engine: AsyncEngine = create_async_engine(
            url=url,
            echo=echo,
        )

        self._session_factory: async_sessionmaker = async_sessionmaker(
            bind=self._engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    async def session_dependency(self) -> AsyncGenerator[Any, Any]:
        async with self._session_factory() as session:
            yield session
            await session.close()


def database_factory(database_config: DatabaseConfig) -> DatabaseSQLAlchemy:
    return DatabaseSQLAlchemy(
        url=database_config.database_url_asyncpg,
        echo=database_config.ECHO,
    )
