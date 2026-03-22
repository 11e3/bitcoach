import asyncio
import uuid
from contextlib import asynccontextmanager

from fastapi import Cookie, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import delete

from app.api.routes import analysis, coaching, trades
from app.config import get_settings
from app.db.database import async_session, init_db
from app.models.trade import Trade

SESSION_TTL_HOURS = 24


async def cleanup_old_sessions():
    """Delete trades from sessions older than TTL."""
    import datetime

    cutoff = datetime.datetime.utcnow() - datetime.timedelta(hours=SESSION_TTL_HOURS)
    async with async_session() as db:
        await db.execute(delete(Trade).where(Trade.created_at < cutoff))
        await db.commit()


async def periodic_cleanup():
    """Run cleanup every hour."""
    while True:
        await asyncio.sleep(3600)
        try:
            await cleanup_old_sessions()
        except Exception:
            pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup, run periodic cleanup."""
    await init_db()
    task = asyncio.create_task(periodic_cleanup())
    yield
    task.cancel()


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

    @app.middleware("http")
    async def session_middleware(request: Request, call_next):
        """Auto-assign session_id cookie if not present."""
        session_id = request.cookies.get("session_id")
        if not session_id:
            session_id = uuid.uuid4().hex
        request.state.session_id = session_id
        response: Response = await call_next(request)
        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            samesite="none",
            secure=True,
            max_age=SESSION_TTL_HOURS * 3600,
        )
        return response

    # Routes
    app.include_router(trades.router, prefix="/api/trades", tags=["trades"])
    app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
    app.include_router(coaching.router, prefix="/api/coaching", tags=["coaching"])

    @app.get("/api/health")
    async def health_check():
        return {"status": "ok", "version": "0.1.0"}

    return app


app = create_app()
