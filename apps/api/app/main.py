from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.router import api_router
from app.core.config import settings
from app.db.session import get_db
from app.observability.metrics import render_runtime_metrics
from app.observability.middleware import MetricsMiddleware
from app.core.runtime import configure_runtime
from app.realtime.manager import realtime_manager
from app.workers.queue import queue_client

configure_runtime()


@asynccontextmanager
async def lifespan(_: FastAPI):
    await realtime_manager.connect()
    yield
    await realtime_manager.disconnect()


app = FastAPI(
    title="Global Intelligence Platform API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(MetricsMiddleware)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
async def readiness(db: AsyncSession = Depends(get_db)):
    checks: dict[str, object] = {}
    status_code = 200

    try:
        await db.execute(text("select 1"))
        checks["database"] = "ok"
    except Exception as exc:
        checks["database"] = f"error: {exc.__class__.__name__}"
        status_code = 503

    try:
        checks["redis"] = "ok"
        checks["crawl_queue_depth"] = await queue_client.size("crawl:jobs")
    except Exception as exc:
        checks["redis"] = f"error: {exc.__class__.__name__}"
        status_code = 503

    payload = {"status": "ok" if status_code == 200 else "degraded", "checks": checks}
    if status_code != 200:
        return JSONResponse(status_code=status_code, content=payload)
    return payload


@app.get("/metrics", response_class=PlainTextResponse)
async def metrics(db: AsyncSession = Depends(get_db)) -> str:
    return await render_runtime_metrics(db)
