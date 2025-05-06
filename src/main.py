import uvicorn
from fastapi import FastAPI

from src.config import settings

main_app = FastAPI(title="Business Management System")


if __name__ == "__main__":
    uvicorn.run("main:main_app", host=settings.run.host, port=settings.run.port, reload=True)
