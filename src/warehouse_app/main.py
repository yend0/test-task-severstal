import uvicorn

from warehouse_app.core.config import Config

if __name__ == "__main__":
    uvicorn.run(
        "warehouse_app.app:create_app",
        host=Config.uvicorn.HOST,
        port=Config.uvicorn.PORT,
        factory=Config.uvicorn.FACTORY,
        reload=Config.uvicorn.RELOAD,
        log_level=Config.uvicorn.LOG_LEVEL,
    )