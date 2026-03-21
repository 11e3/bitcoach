from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.services.trade_analyzer import (
    FullAnalysis,
    compute_coin_performance,
    compute_time_analysis,
    compute_weekday_analysis,
    get_all_trades,
    run_full_analysis,
)

router = APIRouter()


@router.get("/full", response_model=FullAnalysis)
async def full_analysis(db: AsyncSession = Depends(get_db)):
    """Run complete trade analysis."""
    return await run_full_analysis(db)


@router.get("/by-coin")
async def analysis_by_coin(db: AsyncSession = Depends(get_db)):
    """Per-coin performance analysis."""
    trades = await get_all_trades(db)
    return compute_coin_performance(trades)


@router.get("/by-time")
async def analysis_by_time(db: AsyncSession = Depends(get_db)):
    """Time-of-day performance analysis."""
    trades = await get_all_trades(db)
    return compute_time_analysis(trades)


@router.get("/by-weekday")
async def analysis_by_weekday(db: AsyncSession = Depends(get_db)):
    """Day-of-week performance analysis."""
    trades = await get_all_trades(db)
    return compute_weekday_analysis(trades)
