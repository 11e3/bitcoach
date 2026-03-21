import datetime
import json

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.trade import CoachingReport
from app.services.coaching_agent import run_coaching_pipeline

router = APIRouter()


# --- Schemas ---


class ActionItemOut(BaseModel):
    action: str
    priority: str
    metric: str
    timeframe: str


class CoachingReportOut(BaseModel):
    id: int
    summary: str
    strengths: str
    weaknesses: str
    suggestions: str
    action_items: list[ActionItemOut]
    trade_count: int
    period_start: datetime.datetime | None
    period_end: datetime.datetime | None
    created_at: datetime.datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_db(cls, report: CoachingReport) -> "CoachingReportOut":
        try:
            actions = json.loads(report.action_items) if report.action_items else []
        except json.JSONDecodeError:
            actions = []

        return cls(
            id=report.id,
            summary=report.summary,
            strengths=report.strengths,
            weaknesses=report.weaknesses,
            suggestions=report.suggestions,
            action_items=[ActionItemOut(**a) for a in actions],
            trade_count=report.trade_count,
            period_start=report.period_start,
            period_end=report.period_end,
            created_at=report.created_at,
        )


class GenerateRequest(BaseModel):
    start: datetime.datetime | None = None
    end: datetime.datetime | None = None


class GenerateResponse(BaseModel):
    report_id: int
    summary: str
    trade_count: int


# --- Routes ---


@router.post("/generate", response_model=GenerateResponse)
async def generate_report(
    request: GenerateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Generate a new AI coaching report via LangGraph pipeline.

    Pipeline: classify (Haiku) → statistics (Python) → patterns (Haiku)
              → coaching (Sonnet) → actions (Sonnet)
    """
    try:
        report = await run_coaching_pipeline(
            db=db,
            start=request.start,
            end=request.end,
        )
        await db.commit()

        return GenerateResponse(
            report_id=report.id,
            summary=report.summary[:200],
            trade_count=report.trade_count,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"코칭 생성 실패: {str(e)}")


@router.get("/reports")
async def list_reports(
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List past coaching reports."""
    result = await db.execute(
        select(CoachingReport)
        .order_by(CoachingReport.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    reports = result.scalars().all()
    return [CoachingReportOut.from_db(r) for r in reports]


@router.get("/reports/{report_id}")
async def get_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific coaching report."""
    result = await db.execute(
        select(CoachingReport).where(CoachingReport.id == report_id)
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return CoachingReportOut.from_db(report)
