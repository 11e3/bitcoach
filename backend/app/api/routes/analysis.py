from fastapi import APIRouter, Depends, Request
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


def get_session_id(request: Request) -> str:
    return getattr(request.state, "session_id", "")


@router.get("/full", response_model=FullAnalysis)
async def full_analysis(request: Request, db: AsyncSession = Depends(get_db)):
    return await run_full_analysis(db, session_id=get_session_id(request))


@router.get("/by-coin")
async def analysis_by_coin(request: Request, db: AsyncSession = Depends(get_db)):
    trades = await get_all_trades(db, session_id=get_session_id(request))
    return compute_coin_performance(trades)


@router.get("/by-time")
async def analysis_by_time(request: Request, db: AsyncSession = Depends(get_db)):
    trades = await get_all_trades(db, session_id=get_session_id(request))
    return compute_time_analysis(trades)


@router.get("/by-weekday")
async def analysis_by_weekday(request: Request, db: AsyncSession = Depends(get_db)):
    trades = await get_all_trades(db, session_id=get_session_id(request))
    return compute_weekday_analysis(trades)
