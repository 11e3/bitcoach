"""Coaching service — orchestrates LangGraph pipeline, returns results directly."""

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.graph import coaching_pipeline
from app.agents.state import CoachingState, TradeRecord
from app.models.trade import Trade


@dataclass
class CoachingResult:
    summary: str
    strengths: str
    weaknesses: str
    suggestions: str
    action_items: list[dict]
    trade_count: int
    period_start: datetime | None
    period_end: datetime | None


async def run_coaching_pipeline(
    db: AsyncSession,
    start: datetime | None = None,
    end: datetime | None = None,
) -> CoachingResult:
    """Run the full coaching pipeline and return results (no DB storage).

    Pipeline: classify (Haiku) → statistics (Python) → patterns (Haiku)
              → coaching (Haiku) → actions (Haiku)
    """
    query = select(Trade).order_by(Trade.traded_at.asc())
    if start:
        query = query.where(Trade.traded_at >= start)
    if end:
        query = query.where(Trade.traded_at <= end)

    result = await db.execute(query)
    trades = list(result.scalars().all())

    if not trades:
        raise ValueError("분석할 거래내역이 없습니다.")

    trade_records = [
        TradeRecord(
            uuid=t.uuid,
            market=t.market,
            side=t.side,
            price=t.price,
            volume=t.volume,
            funds=t.funds,
            fee=t.fee,
            traded_at=t.traded_at.isoformat() if isinstance(t.traded_at, datetime) else str(t.traded_at),
        )
        for t in trades
    ]

    initial_state = CoachingState(trades=trade_records)

    result = await coaching_pipeline.ainvoke(initial_state)

    if isinstance(result, dict):
        final_state = CoachingState(**result)
    else:
        final_state = result

    return CoachingResult(
        summary=final_state.report_summary,
        strengths=final_state.report_strengths,
        weaknesses=final_state.report_weaknesses,
        suggestions=final_state.report_suggestions,
        action_items=[a.model_dump() for a in final_state.action_items],
        trade_count=len(trades),
        period_start=trades[0].traded_at if trades else None,
        period_end=trades[-1].traded_at if trades else None,
    )
