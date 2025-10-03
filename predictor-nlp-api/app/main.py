from fastapi import FastAPI
from app.core.config import settings
from app.core.logging import setup_logging
from app.api.routers import health, predict, preview, admin
from prometheus_fastapi_instrumentator import Instrumentator

setup_logging()
app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

Instrumentator().instrument(app).expose(app, endpoint="/metrics")

app.include_router(health.router)
app.include_router(predict.router)
app.include_router(preview.router)
app.include_router(admin.router)
