import asyncio
import uuid
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import delete

from app.api.routes import analysis, coaching, trades
from app.config import get_settings
from app.db.database import async_session, get_db, init_db
from sqlalchemy.ext.asyncio import AsyncSession
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

    @app.get("/api/stats")
    async def usage_stats(db: AsyncSession = Depends(get_db)):
        """Public usage stats for portfolio."""
        from sqlalchemy import func, select
        from app.models.trade import AnalyticsEvent
        result = await db.execute(
            select(
                AnalyticsEvent.event,
                func.count(AnalyticsEvent.id).label("count"),
                func.count(func.distinct(AnalyticsEvent.session_id)).label("sessions"),
            ).group_by(AnalyticsEvent.event)
        )
        rows = {r.event: {"count": r.count, "unique_sessions": r.sessions} for r in result.all()}
        return rows

    return app


app = create_app()
