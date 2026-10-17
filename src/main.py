from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from src.admin.admin_setup import setup_admin
from src.config import settings
from src.models import dbh
from src.routers import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # shutdown
    await dbh.dispose()


main_app = FastAPI(title="Business Management System", lifespan=lifespan)
main_app.include_router(router)
setup_admin(main_app)

if __name__ == "__main__":
    uvicorn.run(
        "src.main:main_app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
