import uvicorn
from fastapi import FastAPI

from src.config import settings
from src.routers import router

main_app = FastAPI(title="Business Management System")
main_app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:main_app", host=settings.run.host, port=settings.run.port, reload=True)
