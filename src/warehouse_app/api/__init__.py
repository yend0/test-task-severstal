from enum import Enum

from fastapi.routing import APIRouter

from warehouse_app.api import rest
from warehouse_app.core.config import Config


class Tags(Enum):
    ROLLS = "Rolls"


api_router = APIRouter(prefix=f"{Config.urls.API_PREFIX}")
api_router.include_router(rest.router, prefix="/rolls", tags=[Tags.ROLLS])
