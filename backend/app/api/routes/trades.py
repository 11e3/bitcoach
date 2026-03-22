import datetime

from fastapi import APIRouter, Cookie, Depends, File, HTTPException, Query, Response, UploadFile
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.csv_parser import parse_csv
from app.core.events_parser import parse_events
from app.core.paste_parser import parse_paste
from app.core.security import credential_manager
from app.core.upbit_client import UpbitCredentials
from app.db.database import get_db
from app.models.trade import Trade

router = APIRouter()


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


class ConnectRequest(BaseModel):
    access_key: str
    secret_key: str


class ConnectResponse(BaseModel):
    success: bool
    message: str
    balance_count: int = 0


class SyncResponse(BaseModel):
    synced: int
    skipped: int
    total: int
    market_orders_enriched: int = 0


# --- Auth helpers ---


def get_session_token(session_token: str | None = Cookie(None)) -> str:
    if not session_token:
        raise HTTPException(status_code=401, detail="Not connected. Submit API keys first.")
    return session_token


# --- Routes ---


@router.post("/connect", response_model=ConnectResponse)
async def connect_upbit(request: ConnectRequest, response: Response):
    """Submit API keys. Stored in server memory only, never on disk."""
    credentials = UpbitCredentials(
        access_key=request.access_key,
        secret_key=request.secret_key,
    )
    token = credential_manager.create_session(credentials)
    client = credential_manager.get_client(token)

    if client is None:
        raise HTTPException(status_code=500, detail="Failed to create session")

    try:
        accounts = await client.get_accounts()
    except Exception:
        await credential_manager.remove_session(token)
        raise HTTPException(status_code=401, detail="업비트 API 인증 실패.")

    response.set_cookie(
        key="session_token", value=token,
        httponly=True, samesite="lax", max_age=3600,
    )
    return ConnectResponse(success=True, message="업비트 연결 성공", balance_count=len(accounts))


@router.post("/disconnect")
async def disconnect_upbit(response: Response, session_token: str = Depends(get_session_token)):
    """Clear API keys from memory."""
    await credential_manager.remove_session(session_token)
    response.delete_cookie("session_token")
    return {"message": "API 키가 메모리에서 삭제되었습니다."}


def _parse_order(order: dict) -> dict:
    """Extract trade fields from an Upbit order response.

    Priority:
    1. trades field (individual fills) — most accurate for market orders
    2. executed_funds — available on some endpoints
    3. price × volume — works for limit orders
    """
    side = "buy" if order.get("side") == "bid" else "sell"
    volume = float(order.get("executed_volume", 0) or 0)
    fee = float(order.get("paid_fee", 0) or 0)

    # 1) trades field (from /v1/order detail enrichment)
    trades_list = order.get("trades", [])
    if trades_list:
        funds = sum(float(t.get("funds", 0) or 0) for t in trades_list)
        price = funds / volume if volume > 0 else 0
    # 2) executed_funds
    elif float(order.get("executed_funds", 0) or 0) > 0:
        funds = float(order["executed_funds"])
        price = funds / volume if volume > 0 else 0
    # 3) price × volume (limit orders)
    else:
        price = float(order.get("price", 0) or 0)
        funds = price * volume

    return {
        "side": side,
        "price": price,
        "volume": volume,
        "funds": funds,
        "fee": fee,
    }


@router.post("/sync", response_model=SyncResponse)
async def sync_trades(db: AsyncSession = Depends(get_db), session_token: str = Depends(get_session_token)):
    """Fetch trades from Upbit via backend proxy."""
    client = credential_manager.get_client(session_token)
    if client is None:
        raise HTTPException(status_code=401, detail="세션 만료. 다시 연결해주세요.")

    try:
        orders = await client.fetch_all_completed_orders()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"업비트 API 호출 실패: {e}")

    synced, skipped = 0, 0
    enriched_count = sum(1 for o in orders if o.get("trades"))

    for order in orders:
        order_uuid = order.get("uuid", "")
        exists = await db.execute(select(Trade.id).where(Trade.uuid == order_uuid))
        if exists.scalar_one_or_none():
            skipped += 1
            continue

        parsed = _parse_order(order)

        # Skip records with no funds or volume (airdrops, delistings, etc.)
        if parsed["funds"] <= 0 or parsed["volume"] <= 0:
            skipped += 1
            continue

        trade = Trade(
            uuid=order_uuid, market=order.get("market", ""), side=parsed["side"],
            price=parsed["price"], volume=parsed["volume"], funds=parsed["funds"],
            fee=parsed["fee"],
            traded_at=datetime.datetime.fromisoformat(order.get("created_at", "")),
        )
        db.add(trade)
        synced += 1

    await db.flush()
    return SyncResponse(
        synced=synced, skipped=skipped, total=synced + skipped,
        market_orders_enriched=enriched_count,
    )


@router.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    """Upload Upbit trade history CSV."""
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="CSV 파일만 업로드 가능합니다.")

    content = await file.read()
    try:
        parsed = parse_csv(content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not parsed:
        raise HTTPException(status_code=400, detail="파싱 가능한 거래내역이 없습니다.")

    synced, skipped = 0, 0
    for td in parsed:
        exists = await db.execute(select(Trade.id).where(Trade.uuid == td.uuid))
        if exists.scalar_one_or_none():
            skipped += 1
            continue

        trade = Trade(
            uuid=td.uuid, market=td.market, side=td.side,
            price=td.price, volume=td.volume, funds=td.funds,
            fee=td.fee, traded_at=td.traded_at,
        )
        db.add(trade)
        synced += 1

    await db.flush()
    return {"synced": synced, "skipped": skipped, "total_parsed": len(parsed)}


class PasteRequest(BaseModel):
    text: str


@router.post("/paste")
async def paste_trades(request: PasteRequest, db: AsyncSession = Depends(get_db)):
    """Import trades from pasted text.

    Supports two formats:
    - JSON array from browser console script (events API format)
    - Plain text copied from Upbit web (10-line trade blocks)
    """
    text = request.text.strip()
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
        if not td.uuid or td.funds <= 0:
            skipped += 1
            continue
        exists = await db.execute(select(Trade.id).where(Trade.uuid == td.uuid))
        if exists.scalar_one_or_none():
            skipped += 1
            continue

        trade = Trade(
            uuid=td.uuid, market=td.market, side=td.side,
            price=td.price, volume=td.volume, funds=td.funds,
            fee=td.fee, traded_at=td.traded_at,
        )
        db.add(trade)
        synced += 1

    await db.flush()
    return {"synced": synced, "skipped": skipped, "total_parsed": len(parsed)}


@router.get("", response_model=list[TradeOut])
async def get_trades(
    market: str | None = Query(None), side: str | None = Query(None),
    start: datetime.datetime | None = Query(None), end: datetime.datetime | None = Query(None),
    limit: int = Query(100, le=1000), offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    query = select(Trade).order_by(Trade.traded_at.desc())
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
async def get_statistics(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(
            func.count(Trade.id).label("total"),
            func.count(Trade.id).filter(Trade.side == "buy").label("buys"),
            func.count(Trade.id).filter(Trade.side == "sell").label("sells"),
            func.count(func.distinct(Trade.market)).label("markets"),
            func.sum(Trade.funds).label("volume"),
            func.min(Trade.traded_at).label("first"),
            func.max(Trade.traded_at).label("last"),
        )
    )
    row = result.one()
    return TradeStats(
        total_trades=row.total or 0, total_buy=row.buys or 0,
        total_sell=row.sells or 0, unique_markets=row.markets or 0,
        total_volume_krw=row.volume or 0.0,
        period_start=row.first, period_end=row.last,
    )
