import datetime
from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.trade import AnalyticsEvent
from app.services.coaching_agent import run_coaching_pipeline

router = APIRouter()

# Rate limit: 5 coaching generations per session per day
_rate_limit: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT_MAX = 5
RATE_LIMIT_WINDOW = 86400  # 24 hours


def _check_rate_limit(session_id: str) -> None:
    import time

    now = time.time()
    times = _rate_limit[session_id]
    # Remove old entries
    _rate_limit[session_id] = [t for t in times if now - t < RATE_LIMIT_WINDOW]
    if len(_rate_limit[session_id]) >= RATE_LIMIT_MAX:
        raise HTTPException(
            status_code=429,
            detail=f"코칭 생성은 하루 {RATE_LIMIT_MAX}회로 제한됩니다.",
        )
    _rate_limit[session_id].append(now)


# --- Schemas ---


class ActionItemOut(BaseModel):
    action: str
    priority: str
    metric: str
    timeframe: str


class CoachingReportOut(BaseModel):
    summary: str
    strengths: str
    weaknesses: str
    suggestions: str
    action_items: list[ActionItemOut]
    trade_count: int
    period_start: datetime.datetime | None
    period_end: datetime.datetime | None


class GenerateRequest(BaseModel):
    start: datetime.datetime | None = None
    end: datetime.datetime | None = None


# --- Routes ---


@router.post("/generate", response_model=CoachingReportOut)
async def generate_report(
    request: Request,
    body: GenerateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Generate AI coaching report via LangGraph pipeline.

    Rate limited to 5 per session per day.
    """
    session_id = getattr(request.state, "session_id", "")
    _check_rate_limit(session_id)

    try:
        report = await run_coaching_pipeline(
            db=db,
            session_id=session_id,
            start=body.start,
            end=body.end,
        )
        db.add(AnalyticsEvent(event="coaching", session_id=session_id))
        await db.flush()
        return report
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"코칭 생성 실패: {str(e)}")
