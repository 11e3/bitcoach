"""Trade analysis engine.

Pure Python computation — no LLM calls.
Computes statistics, detects patterns, and prepares data for AI coaching.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trade import Trade


# --- Output Schemas ---


class CoinPerformance(BaseModel):
    market: str
    trade_count: int
    buy_count: int
    sell_count: int
    total_buy_funds: float
    total_sell_funds: float
    total_fees: float
    realized_pnl: float
    pnl_pct: float
    avg_hold_period_hours: float | None = None


class TimeSlotPerformance(BaseModel):
    hour: int  # 0-23
    trade_count: int
    buy_count: int
    sell_count: int
    avg_funds: float


class WeekdayPerformance(BaseModel):
    weekday: int  # 0=Monday, 6=Sunday
    weekday_name: str
    trade_count: int
    buy_count: int
    sell_count: int


class HoldingPeriod(BaseModel):
    bucket: str  # "< 1h", "1-6h", "6-24h", "1-3d", "3-7d", "7d+"
    count: int
    pct: float


class OverallStats(BaseModel):
    total_trades: int
    total_buy: int
    total_sell: int
    unique_markets: int
    total_buy_funds: float
    total_sell_funds: float
    total_fees: float
    realized_pnl: float
    win_rate: float  # % of profitable coin pairs
    period_start: datetime | None
    period_end: datetime | None
    active_days: int
    avg_trades_per_day: float


class FullAnalysis(BaseModel):
    overall: OverallStats
    by_coin: list[CoinPerformance]
    by_hour: list[TimeSlotPerformance]
    by_weekday: list[WeekdayPerformance]
    holding_periods: list[HoldingPeriod]
    top_winners: list[CoinPerformance]
    top_losers: list[CoinPerformance]


# --- Analyzer ---


WEEKDAY_NAMES_KO = ["월", "화", "수", "목", "금", "토", "일"]

HOLD_BUCKETS = [
    (1, "< 1시간"),
    (6, "1-6시간"),
    (24, "6-24시간"),
    (72, "1-3일"),
    (168, "3-7일"),
    (float("inf"), "7일+"),
]


@dataclass
class TradePair:
    """Matched buy-sell pair for a single coin."""

    market: str
    buy_time: datetime
    sell_time: datetime
    buy_funds: float
    sell_funds: float
    buy_fee: float
    sell_fee: float

    @property
    def pnl(self) -> float:
        return self.sell_funds - self.buy_funds - self.buy_fee - self.sell_fee

    @property
    def pnl_pct(self) -> float:
        if self.buy_funds == 0:
            return 0.0
        return (self.pnl / self.buy_funds) * 100

    @property
    def hold_hours(self) -> float:
        return (self.sell_time - self.buy_time).total_seconds() / 3600


async def get_all_trades(db: AsyncSession, session_id: str = "") -> list[Trade]:
    """Fetch all trades for a session, ordered by time."""
    query = select(Trade).where(Trade.funds > 0).order_by(Trade.traded_at.asc())
    if session_id:
        query = query.where(Trade.session_id == session_id)
    result = await db.execute(query)
    return list(result.scalars().all())


@dataclass
class _BuySlot:
    """Remaining portion of a buy trade in the FIFO queue."""

    trade: Trade
    remaining_volume: float


def match_trade_pairs(trades: list[Trade]) -> list[TradePair]:
    """Match buy/sell pairs per market using volume-based FIFO.

    Handles partial fills: a single sell can consume multiple buys,
    and a single buy can be split across multiple sells.
    """
    buy_queue: dict[str, list[_BuySlot]] = {}
    pairs: list[TradePair] = []

    for trade in trades:
        if trade.side == "buy":
            buy_queue.setdefault(trade.market, []).append(
                _BuySlot(trade=trade, remaining_volume=trade.volume)
            )
        elif trade.side == "sell":
            queue = buy_queue.get(trade.market, [])
            sell_remaining = trade.volume
            sell_price = trade.price
            sell_fee_rate = trade.fee / trade.funds if trade.funds > 0 else 0.0

            while sell_remaining > 1e-12 and queue:
                slot = queue[0]
                matched_vol = min(sell_remaining, slot.remaining_volume)
                fraction_of_buy = matched_vol / slot.trade.volume if slot.trade.volume > 0 else 0.0
                fraction_of_sell = matched_vol / trade.volume if trade.volume > 0 else 0.0

                buy_funds = slot.trade.price * matched_vol
                sell_funds = sell_price * matched_vol
                buy_fee = slot.trade.fee * fraction_of_buy
                sell_fee = trade.fee * fraction_of_sell

                pairs.append(
                    TradePair(
                        market=trade.market,
                        buy_time=slot.trade.traded_at,
                        sell_time=trade.traded_at,
                        buy_funds=buy_funds,
                        sell_funds=sell_funds,
                        buy_fee=buy_fee,
                        sell_fee=sell_fee,
                    )
                )

                slot.remaining_volume -= matched_vol
                sell_remaining -= matched_vol

                if slot.remaining_volume <= 1e-12:
                    queue.pop(0)

    return pairs


def compute_coin_performance(trades: list[Trade]) -> list[CoinPerformance]:
    """Compute per-coin statistics using FIFO-matched pairs for PnL."""
    # Basic counts per market
    markets: dict[str, dict] = {}
    for trade in trades:
        m = markets.setdefault(
            trade.market,
            {"buy_count": 0, "sell_count": 0, "total_buy_funds": 0.0, "total_sell_funds": 0.0, "total_fees": 0.0},
        )
        if trade.side == "buy":
            m["buy_count"] += 1
            m["total_buy_funds"] += trade.funds
        else:
            m["sell_count"] += 1
            m["total_sell_funds"] += trade.funds
        m["total_fees"] += trade.fee

    # FIFO matching for realized PnL
    pairs = match_trade_pairs(trades)
    pnl_by_market: dict[str, float] = {}
    matched_buy_funds: dict[str, float] = {}
    hold_hours_by_market: dict[str, list[float]] = {}
    for pair in pairs:
        pnl_by_market[pair.market] = pnl_by_market.get(pair.market, 0.0) + pair.pnl
        matched_buy_funds[pair.market] = matched_buy_funds.get(pair.market, 0.0) + pair.buy_funds
        hold_hours_by_market.setdefault(pair.market, []).append(pair.hold_hours)

    results = []
    for market, stats in markets.items():
        if stats["buy_count"] == 0:
            continue
        pnl = pnl_by_market.get(market, 0.0)
        matched_buys = matched_buy_funds.get(market, 0.0)
        pnl_pct = (pnl / matched_buys * 100) if matched_buys > 0 else 0.0
        hours = hold_hours_by_market.get(market)
        avg_hold = sum(hours) / len(hours) if hours else None

        results.append(
            CoinPerformance(
                market=market,
                trade_count=stats["buy_count"] + stats["sell_count"],
                buy_count=stats["buy_count"],
                sell_count=stats["sell_count"],
                total_buy_funds=stats["total_buy_funds"],
                total_sell_funds=stats["total_sell_funds"],
                total_fees=stats["total_fees"],
                realized_pnl=round(pnl, 0),
                pnl_pct=round(pnl_pct, 2),
                avg_hold_period_hours=round(avg_hold, 1) if avg_hold is not None else None,
            )
        )

    return sorted(results, key=lambda x: x.realized_pnl, reverse=True)


def compute_time_analysis(trades: list[Trade]) -> list[TimeSlotPerformance]:
    """Analyze trading activity by hour of day."""
    hours: dict[int, dict] = {h: {"buy": 0, "sell": 0, "funds": []} for h in range(24)}

    for trade in trades:
        h = trade.traded_at.hour
        if trade.side == "buy":
            hours[h]["buy"] += 1
        else:
            hours[h]["sell"] += 1
        hours[h]["funds"].append(trade.funds)

    results = []
    for hour, stats in hours.items():
        total = stats["buy"] + stats["sell"]
        funds_list = stats["funds"]
        results.append(
            TimeSlotPerformance(
                hour=hour,
                trade_count=total,
                buy_count=stats["buy"],
                sell_count=stats["sell"],
                avg_funds=sum(funds_list) / len(funds_list) if funds_list else 0.0,
            )
        )

    return results


def compute_weekday_analysis(trades: list[Trade]) -> list[WeekdayPerformance]:
    """Analyze trading activity by day of week."""
    days: dict[int, dict] = {d: {"buy": 0, "sell": 0} for d in range(7)}

    for trade in trades:
        d = trade.traded_at.weekday()
        if trade.side == "buy":
            days[d]["buy"] += 1
        else:
            days[d]["sell"] += 1

    return [
        WeekdayPerformance(
            weekday=d,
            weekday_name=WEEKDAY_NAMES_KO[d],
            trade_count=stats["buy"] + stats["sell"],
            buy_count=stats["buy"],
            sell_count=stats["sell"],
        )
        for d, stats in days.items()
    ]


def compute_holding_periods(pairs: list[TradePair]) -> list[HoldingPeriod]:
    """Compute holding period distribution."""
    if not pairs:
        return []

    buckets: dict[str, int] = {label: 0 for _, label in HOLD_BUCKETS}

    for pair in pairs:
        hours = pair.hold_hours
        for threshold, label in HOLD_BUCKETS:
            if hours < threshold:
                buckets[label] += 1
                break

    total = len(pairs)
    return [
        HoldingPeriod(
            bucket=label,
            count=count,
            pct=round(count / total * 100, 1) if total > 0 else 0.0,
        )
        for label, count in buckets.items()
    ]


async def run_full_analysis(db: AsyncSession, session_id: str = "") -> FullAnalysis:
    """Run complete trade analysis."""
    trades = await get_all_trades(db, session_id=session_id)

    if not trades:
        return FullAnalysis(
            overall=OverallStats(
                total_trades=0, total_buy=0, total_sell=0,
                unique_markets=0, total_buy_funds=0, total_sell_funds=0,
                total_fees=0, realized_pnl=0, win_rate=0,
                period_start=None, period_end=None,
                active_days=0, avg_trades_per_day=0,
            ),
            by_coin=[], by_hour=[], by_weekday=[],
            holding_periods=[], top_winners=[], top_losers=[],
        )

    # Compute pairs
    pairs = match_trade_pairs(trades)

    # Per-coin
    coin_perf = compute_coin_performance(trades)
    coins_with_sells = [c for c in coin_perf if c.sell_count > 0]
    # Win rate based on individual FIFO-matched trade pairs, not per-coin
    winning_pairs = [p for p in pairs if p.pnl > 0]
    win_rate = len(winning_pairs) / len(pairs) * 100 if pairs else 0.0

    # Time analysis
    by_hour = compute_time_analysis(trades)
    by_weekday = compute_weekday_analysis(trades)

    # Holding periods
    holding_periods = compute_holding_periods(pairs)

    # Overall
    buys = [t for t in trades if t.side == "buy"]
    sells = [t for t in trades if t.side == "sell"]
    total_buy_funds = sum(t.funds for t in buys)
    total_sell_funds = sum(t.funds for t in sells)
    total_fees = sum(t.fee for t in trades)

    # Calendar days (not just active trading days)
    calendar_days = (trades[-1].traded_at - trades[0].traded_at).days + 1

    overall = OverallStats(
        total_trades=len(trades),
        total_buy=len(buys),
        total_sell=len(sells),
        unique_markets=len(set(t.market for t in trades)),
        total_buy_funds=round(total_buy_funds, 0),
        total_sell_funds=round(total_sell_funds, 0),
        total_fees=round(total_fees, 0),
        realized_pnl=round(sum(p.pnl for p in pairs), 0),
        win_rate=round(win_rate, 1),
        period_start=trades[0].traded_at,
        period_end=trades[-1].traded_at,
        active_days=calendar_days,
        avg_trades_per_day=round(len(trades) / calendar_days, 1) if calendar_days > 0 else 0,
    )

    return FullAnalysis(
        overall=overall,
        by_coin=coin_perf,
        by_hour=by_hour,
        by_weekday=by_weekday,
        holding_periods=holding_periods,
        top_winners=sorted(coins_with_sells, key=lambda x: x.realized_pnl, reverse=True)[:5],
        top_losers=sorted(coins_with_sells, key=lambda x: x.realized_pnl)[:5],
    )
