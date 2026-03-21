"""Tests for trade analyzer service."""

import datetime

import pytest

from app.services.trade_analyzer import (
    TradePair,
    compute_holding_periods,
    match_trade_pairs,
)


class FakeTrade:
    """Minimal trade object for testing."""

    def __init__(self, uuid, market, side, price, volume, funds, fee, traded_at):
        self.uuid = uuid
        self.market = market
        self.side = side
        self.price = price
        self.volume = volume
        self.funds = funds
        self.fee = fee
        self.traded_at = traded_at


def test_match_trade_pairs_fifo():
    trades = [
        FakeTrade("1", "KRW-BTC", "buy", 50000000, 0.01, 500000, 250, datetime.datetime(2024, 1, 1, 10, 0)),
        FakeTrade("2", "KRW-BTC", "sell", 52000000, 0.01, 520000, 260, datetime.datetime(2024, 1, 2, 10, 0)),
    ]

    pairs = match_trade_pairs(trades)
    assert len(pairs) == 1
    assert pairs[0].market == "KRW-BTC"
    assert pairs[0].pnl == 520000 - 500000 - 250 - 260  # 19490
    assert pairs[0].hold_hours == pytest.approx(24.0)


def test_match_trade_pairs_multiple_coins():
    trades = [
        FakeTrade("1", "KRW-BTC", "buy", 50000000, 0.01, 500000, 250, datetime.datetime(2024, 1, 1)),
        FakeTrade("2", "KRW-ETH", "buy", 3000000, 0.1, 300000, 150, datetime.datetime(2024, 1, 1)),
        FakeTrade("3", "KRW-BTC", "sell", 52000000, 0.01, 520000, 260, datetime.datetime(2024, 1, 2)),
        FakeTrade("4", "KRW-ETH", "sell", 2800000, 0.1, 280000, 140, datetime.datetime(2024, 1, 2)),
    ]

    pairs = match_trade_pairs(trades)
    assert len(pairs) == 2

    btc_pair = next(p for p in pairs if p.market == "KRW-BTC")
    eth_pair = next(p for p in pairs if p.market == "KRW-ETH")

    assert btc_pair.pnl > 0  # Profit
    assert eth_pair.pnl < 0  # Loss


def test_trade_pair_pnl_pct():
    pair = TradePair(
        market="KRW-BTC",
        buy_time=datetime.datetime(2024, 1, 1),
        sell_time=datetime.datetime(2024, 1, 2),
        buy_funds=1000000,
        sell_funds=1100000,
        buy_fee=500,
        sell_fee=550,
    )
    # PnL = 1100000 - 1000000 - 500 - 550 = 98950
    assert pair.pnl == 98950
    assert pair.pnl_pct == pytest.approx(9.895)


def test_holding_periods_distribution():
    pairs = [
        TradePair("A", datetime.datetime(2024, 1, 1, 10), datetime.datetime(2024, 1, 1, 10, 30),
                   100000, 101000, 50, 50),  # 0.5h -> < 1h
        TradePair("B", datetime.datetime(2024, 1, 1, 10), datetime.datetime(2024, 1, 1, 13),
                   100000, 99000, 50, 50),  # 3h -> 1-6h
        TradePair("C", datetime.datetime(2024, 1, 1, 10), datetime.datetime(2024, 1, 3, 10),
                   100000, 105000, 50, 50),  # 48h -> 1-3d
    ]

    result = compute_holding_periods(pairs)
    buckets = {h.bucket: h.count for h in result}

    assert buckets["< 1시간"] == 1
    assert buckets["1-6시간"] == 1
    assert buckets["1-3일"] == 1
