from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.core.config import get_settings
from app.jobs.scheduler import scheduler_manager


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    if settings.enable_scheduler:
        scheduler_manager.start()
    yield
    if settings.enable_scheduler:
        scheduler_manager.shutdown()


app = FastAPI(title="Scoutkat API", version="0.1.0", lifespan=lifespan)
app.include_router(router)

