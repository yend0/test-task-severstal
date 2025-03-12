from dataclasses import dataclass

from pydantic_settings import BaseSettings


@dataclass(frozen=True)
class URLPathsConfig:
    API_PREFIX: str = "/api"
    DOCS_URL: str = "/swagger-ui"
    REDOC_URL: str = "/redoc"


class FastAPIConfig(BaseSettings):
    TITLE: str = "Warehouse rolls REST API"
    DESCRIPTION: str = "REST API for test task severstal"
    API_VERSION: str = "0.0.0"


class DatabaseConfig(BaseSettings):
    DATABASE: str
    DATABASE_PORT: int
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_DB: str
    DATABASE_ADDRESS: str
    ECHO: bool = False

    @property
    def database_url_asyncpg(self) -> str:
        return f"{self.DATABASE}+asyncpg://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_ADDRESS}:{self.DATABASE_PORT}/{self.DATABASE_DB}"


class UvicornConfig(BaseSettings):
    HOST: str = "localhost"
    PORT: int = 8000
    LOG_LEVEL: str = "info"
    RELOAD: bool = True
    FACTORY: bool = True


class Config:
    """
    Main configuration class for the application.
    """

    fastapi: FastAPIConfig = FastAPIConfig()
    database: DatabaseConfig = DatabaseConfig()
    uvicorn: UvicornConfig = UvicornConfig()
    urls: URLPathsConfig = URLPathsConfig()
