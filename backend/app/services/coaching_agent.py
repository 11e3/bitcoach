"""Coaching service — orchestrates LangGraph pipeline and persists results."""

import json
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.graph import coaching_pipeline
from app.agents.state import CoachingState, TradeRecord
from app.models.trade import CoachingReport, Trade


async def run_coaching_pipeline(
    db: AsyncSession,
    start: datetime | None = None,
    end: datetime | None = None,
) -> CoachingReport:
    """Run the full coaching pipeline and save the report.

    1. Fetch trades from DB
    2. Convert to agent state
    3. Run LangGraph pipeline
    4. Save report to DB
    5. Update trade classifications
    """

    # Fetch trades
    query = select(Trade).order_by(Trade.traded_at.asc())
    if start:
        query = query.where(Trade.traded_at >= start)
    if end:
        query = query.where(Trade.traded_at <= end)

    result = await db.execute(query)
    trades = list(result.scalars().all())

    if not trades:
        raise ValueError("분석할 거래내역이 없습니다.")

    # Convert to agent state
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

    # Run pipeline
    final_state = await coaching_pipeline.ainvoke(initial_state)

    # Save report
    report = CoachingReport(
        summary=final_state.report_summary,
        strengths=final_state.report_strengths,
        weaknesses=final_state.report_weaknesses,
        suggestions=final_state.report_suggestions,
        action_items=json.dumps(
            [a.model_dump() for a in final_state.action_items],
            ensure_ascii=False,
        ),
        trade_count=len(trades),
        period_start=trades[0].traded_at if trades else None,
        period_end=trades[-1].traded_at if trades else None,
    )
    db.add(report)

    # Update trade classifications in DB
    if final_state.classified_trades:
        type_map = {t.uuid: t.trade_type for t in final_state.classified_trades if t.trade_type}
        for trade in trades:
            if trade.uuid in type_map:
                trade.trade_type = type_map[trade.uuid]

    await db.flush()

    return report
