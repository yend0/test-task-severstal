from fastapi import Request
from fastapi.responses import JSONResponse

from warehouse_app.core.exc import DatabaseUnavailableError


async def database_unavailable_exception_handler(request: Request, exc: DatabaseUnavailableError) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content={"message": "Database connection error. Please try again later."},
    )

async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"message": "Technical error. Please try again later."},
    )
