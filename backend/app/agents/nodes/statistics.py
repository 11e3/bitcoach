"""Node 2: Compute statistics (pure Python, no LLM).

This is the same logic as trade_analyzer but adapted for the agent state.
"""

from collections import defaultdict
from datetime import datetime

from app.agents.state import CoachingState, CoinSummary


async def compute_statistics(state: CoachingState) -> CoachingState:
    """Compute trade statistics from classified trades."""
    trades = state.classified_trades or state.trades

    if not trades:
        return state

    # Overall stats
    buys = [t for t in trades if t.side == "buy"]
    sells = [t for t in trades if t.side == "sell"]
    total_buy_funds = sum(t.funds for t in buys)
    total_sell_funds = sum(t.funds for t in sells)
    total_fees = sum(t.fee for t in trades)

    dates = set()
    for t in trades:
        try:
            dates.add(t.traded_at[:10])
        except Exception:
            pass

    state.overall_stats = {
        "total_trades": len(trades),
        "total_buy": len(buys),
        "total_sell": len(sells),
        "unique_markets": len(set(t.market for t in trades)),
        "total_buy_funds": round(total_buy_funds),
        "total_sell_funds": round(total_sell_funds),
        "total_fees": round(total_fees),
        "realized_pnl": round(total_sell_funds - total_buy_funds - total_fees),
        "active_days": len(dates),
        "classification_summary": state.classification_summary,
    }

    # Per-coin performance (FIFO matching)
    buy_queue: dict[str, list] = defaultdict(list)
    coin_pnl: dict[str, float] = defaultdict(float)
    coin_trades: dict[str, int] = defaultdict(int)
    coin_hold_hours: dict[str, list] = defaultdict(list)

    for trade in trades:
        coin_trades[trade.market] += 1
        if trade.side == "buy":
            buy_queue[trade.market].append(trade)
        elif trade.side == "sell" and buy_queue[trade.market]:
            buy = buy_queue[trade.market].pop(0)
            pnl = trade.funds - buy.funds - buy.fee - trade.fee
            coin_pnl[trade.market] += pnl

            try:
                buy_dt = datetime.fromisoformat(buy.traded_at.replace("+09:00", "+09:00"))
                sell_dt = datetime.fromisoformat(trade.traded_at.replace("+09:00", "+09:00"))
                hours = (sell_dt - buy_dt).total_seconds() / 3600
                coin_hold_hours[trade.market].append(hours)
            except Exception:
                pass

    coin_performance = []
    for market in set(t.market for t in trades):
        buy_funds = sum(t.funds for t in trades if t.market == market and t.side == "buy")
        pnl = coin_pnl.get(market, 0)
        pnl_pct = (pnl / buy_funds * 100) if buy_funds > 0 else 0

        hold_list = coin_hold_hours.get(market, [])
        avg_hold = sum(hold_list) / len(hold_list) if hold_list else None

        coin_performance.append(CoinSummary(
            market=market,
            trade_count=coin_trades[market],
            realized_pnl=round(pnl),
            pnl_pct=round(pnl_pct, 2),
            avg_hold_hours=round(avg_hold, 1) if avg_hold else None,
        ))

    state.coin_performance = sorted(coin_performance, key=lambda x: x.realized_pnl, reverse=True)

    # Time analysis
    hour_counts: dict[int, int] = defaultdict(int)
    weekday_counts: dict[int, int] = defaultdict(int)

    for t in trades:
        try:
            dt = datetime.fromisoformat(t.traded_at.replace("+09:00", "+09:00"))
            hour_counts[dt.hour] += 1
            weekday_counts[dt.weekday()] += 1
        except Exception:
            pass

    peak_hour = max(hour_counts, key=hour_counts.get, default=0) if hour_counts else 0
    peak_weekday = max(weekday_counts, key=weekday_counts.get, default=0) if weekday_counts else 0
    weekday_names = ["월", "화", "수", "목", "금", "토", "일"]

    state.time_analysis = {
        "peak_hour": peak_hour,
        "peak_hour_count": hour_counts.get(peak_hour, 0),
        "peak_weekday": weekday_names[peak_weekday],
        "peak_weekday_count": weekday_counts.get(peak_weekday, 0),
        "hour_distribution": dict(hour_counts),
        "weekday_distribution": {weekday_names[k]: v for k, v in weekday_counts.items()},
    }

    return state
