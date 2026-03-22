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

    # Per-coin performance (volume-based FIFO matching)
    # Each buy slot tracks remaining volume for partial matching
    buy_queue: dict[str, list] = defaultdict(list)  # market -> [(trade, remaining_vol)]
    coin_pnl: dict[str, float] = defaultdict(float)
    coin_trades: dict[str, int] = defaultdict(int)
    coin_hold_hours: dict[str, list] = defaultdict(list)

    for trade in trades:
        coin_trades[trade.market] += 1
        if trade.side == "buy":
            buy_queue[trade.market].append([trade, trade.volume])
        elif trade.side == "sell":
            queue = buy_queue.get(trade.market, [])
            if not queue:
                continue

            sell_remaining = trade.volume
            sell_price = trade.price

            while sell_remaining > 1e-12 and queue:
                buy_trade, buy_remaining = queue[0]
                matched_vol = min(buy_remaining, sell_remaining)

                buy_funds = buy_trade.price * matched_vol
                sell_funds = sell_price * matched_vol
                frac_buy = matched_vol / buy_trade.volume if buy_trade.volume > 0 else 0
                frac_sell = matched_vol / trade.volume if trade.volume > 0 else 0
                pnl = sell_funds - buy_funds - buy_trade.fee * frac_buy - trade.fee * frac_sell
                coin_pnl[trade.market] += pnl

                try:
                    buy_dt = datetime.fromisoformat(buy_trade.traded_at.replace("+09:00", "+09:00"))
                    sell_dt = datetime.fromisoformat(trade.traded_at.replace("+09:00", "+09:00"))
                    hours = (sell_dt - buy_dt).total_seconds() / 3600
                    coin_hold_hours[trade.market].append(hours)
                except Exception:
                    pass

                queue[0][1] -= matched_vol
                sell_remaining -= matched_vol
                if queue[0][1] <= 1e-12:
                    queue.pop(0)

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

    # Pre-compute factual summary (Python guarantees correct numbers)
    total_pnl = state.overall_stats.get("realized_pnl", 0)
    pnl_sign = "수익" if total_pnl >= 0 else "손실"

    winners = [c for c in coin_performance if c.realized_pnl > 0]
    losers = [c for c in coin_performance if c.realized_pnl < 0]
    winners_total = sum(c.realized_pnl for c in winners)
    losers_total = sum(c.realized_pnl for c in losers)

    lines = [
        f"## 팩트 요약 (Python 계산, 수정 금지)",
        f"- 총 거래: {len(trades)}건 (매수 {len(buys)}건, 매도 {len(sells)}건)",
        f"- 기간: {trades[0].traded_at[:10]} ~ {trades[-1].traded_at[:10]}",
        f"- 실현 손익: {total_pnl:+,.0f}원 ({pnl_sign})",
        f"- 총 매수액: {total_buy_funds:,.0f}원",
        f"- 총 수수료: {total_fees:,.0f}원",
        f"",
        f"## 종목별 손익 (확정 수치)",
    ]
    for c in coin_performance:
        if c.realized_pnl != 0:
            hold_str = f", 평균보유 {c.avg_hold_hours:.1f}시간" if c.avg_hold_hours else ""
            lines.append(f"- {c.market}: {c.realized_pnl:+,.0f}원 ({c.pnl_pct:+.2f}%), {c.trade_count}건{hold_str}")

    lines.append("")
    lines.append(f"## 수익/손실 요약")
    lines.append(f"- 수익 종목 {len(winners)}개: 합계 {winners_total:+,.0f}원")
    lines.append(f"- 손실 종목 {len(losers)}개: 합계 {losers_total:+,.0f}원")
    lines.append(f"- 최다 거래 시간: {peak_hour}시 ({hour_counts.get(peak_hour, 0)}건)")
    lines.append(f"- 최다 거래 요일: {weekday_names[peak_weekday]} ({weekday_counts.get(peak_weekday, 0)}건)")

    state.precomputed_summary = "\n".join(lines)

    return state
