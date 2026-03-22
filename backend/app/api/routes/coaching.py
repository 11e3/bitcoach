import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.services.coaching_agent import run_coaching_pipeline

router = APIRouter()


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
    request: GenerateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Generate AI coaching report via LangGraph pipeline.

    Pipeline: classify (Haiku) -> statistics (Python) -> patterns (Haiku)
              -> coaching (Haiku) -> actions (Haiku)

    Returns the report directly without saving to DB.
    """
    try:
        report = await run_coaching_pipeline(
            db=db,
            start=request.start,
            end=request.end,
        )
        return report
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"코칭 생성 실패: {str(e)}")
