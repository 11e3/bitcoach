from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import analysis, coaching, trades
from app.config import get_settings
from app.db.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    await init_db()
    yield


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="bitcoach API",
        description="AI-powered trading coach for Upbit spot traders",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routes
    app.include_router(trades.router, prefix="/api/trades", tags=["trades"])
    app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
    app.include_router(coaching.router, prefix="/api/coaching", tags=["coaching"])

    @app.get("/api/health")
    async def health_check():
        return {"status": "ok", "version": "0.1.0"}

    return app


app = create_app()
