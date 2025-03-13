import contextlib
from collections.abc import AsyncIterator

from fastapi import FastAPI

from warehouse_app.api import api_router
from warehouse_app.core.config import Config
from warehouse_app.core.exc import DatabaseUnavailableError
from warehouse_app.core.handlers import database_unavailable_exception_handler, generic_exception_handler


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Runs events before application startup and after application shutdown.

    Args:
        app: FastAPI application instance.
    """
    try:
        yield
    finally:
        pass


def create_app() -> FastAPI:
    """
    Creates and configures the FastAPI application.

    Returns:
        FastAPI: Configured FastAPI application instance.
    """
    app = FastAPI(
        title=Config.fastapi.TITLE,
        description=Config.fastapi.DESCRIPTION,
        version=Config.fastapi.API_VERSION,
        docs_url=Config.urls.DOCS_URL,
        redoc_url=Config.urls.REDOC_URL,
        lifespan=lifespan,
    )

    app.include_router(router=api_router)

    app.add_exception_handler(DatabaseUnavailableError, database_unavailable_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    return app
