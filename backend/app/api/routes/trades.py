import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.events_parser import parse_events
from app.core.paste_parser import parse_paste
from app.db.database import get_db
from app.models.trade import AnalyticsEvent, Trade

router = APIRouter()


def get_session_id(request: Request) -> str:
    return getattr(request.state, "session_id", "")


# --- Schemas ---


class TradeOut(BaseModel):
    id: int
    uuid: str
    market: str
    side: str
    price: float
    volume: float
    funds: float
    fee: float
    traded_at: datetime.datetime
    trade_type: str | None = None

    model_config = {"from_attributes": True}


class TradeStats(BaseModel):
    total_trades: int
    total_buy: int
    total_sell: int
    unique_markets: int
    total_volume_krw: float
    period_start: datetime.datetime | None
    period_end: datetime.datetime | None


# --- Routes ---


class PasteRequest(BaseModel):
    text: str


@router.post("/paste")
async def paste_trades(
    request: Request,
    body: PasteRequest,
    db: AsyncSession = Depends(get_db),
):
    """Import trades from pasted text."""
    sid = get_session_id(request)
    text = body.text.strip()
    try:
        if text.startswith("["):
            parsed = parse_events(text)
        else:
            parsed = parse_paste(text)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"파싱 실패: {e}")

    if not parsed:
        raise HTTPException(status_code=400, detail="거래내역이 없습니다.")

    synced, skipped = 0, 0
    for td in parsed:
        if td.funds <= 0:
            skipped += 1
            continue
        exists = await db.execute(
            select(Trade.id).where(
                Trade.session_id == sid,
                Trade.market == td.market,
                Trade.side == td.side,
                Trade.traded_at == td.traded_at,
                Trade.funds == td.funds,
                Trade.volume == td.volume,
            )
        )
        if exists.scalar_one_or_none():
            skipped += 1
            continue

        trade = Trade(
            uuid=td.uuid, market=td.market, side=td.side,
            price=td.price, volume=td.volume, funds=td.funds,
            fee=td.fee, traded_at=td.traded_at, session_id=sid,
        )
        db.add(trade)
        synced += 1

    if synced > 0:
        db.add(AnalyticsEvent(event="paste", session_id=sid))
    await db.flush()
    return {"synced": synced, "skipped": skipped, "total_parsed": len(parsed)}


@router.get("", response_model=list[TradeOut])
async def get_trades(
    request: Request,
    market: str | None = Query(None), side: str | None = Query(None),
    start: datetime.datetime | None = Query(None), end: datetime.datetime | None = Query(None),
    limit: int = Query(100, le=1000), offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    sid = get_session_id(request)
    query = select(Trade).where(Trade.session_id == sid).order_by(Trade.traded_at.desc())
    if market:
        query = query.where(Trade.market == market)
    if side:
        query = query.where(Trade.side == side)
    if start:
        query = query.where(Trade.traded_at >= start)
    if end:
        query = query.where(Trade.traded_at <= end)
    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/statistics", response_model=TradeStats)
async def get_statistics(request: Request, db: AsyncSession = Depends(get_db)):
    sid = get_session_id(request)
    result = await db.execute(
        select(
            func.count(Trade.id).label("total"),
            func.count(Trade.id).filter(Trade.side == "buy").label("buys"),
            func.count(Trade.id).filter(Trade.side == "sell").label("sells"),
            func.count(func.distinct(Trade.market)).label("markets"),
            func.sum(Trade.funds).label("volume"),
            func.min(Trade.traded_at).label("first"),
            func.max(Trade.traded_at).label("last"),
        ).where(Trade.session_id == sid)
    )
    row = result.one()
    return TradeStats(
        total_trades=row.total or 0, total_buy=row.buys or 0,
        total_sell=row.sells or 0, unique_markets=row.markets or 0,
        total_volume_krw=row.volume or 0.0,
        period_start=row.first, period_end=row.last,
    )
