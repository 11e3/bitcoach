"""Tests for agent state and pipeline structure."""

import pytest

from app.agents.state import (
    ActionItem,
    CoachingState,
    CoinSummary,
    PatternInfo,
    TradeRecord,
)


def test_coaching_state_defaults():
    state = CoachingState()
    assert state.trades == []
    assert state.classified_trades == []
    assert state.patterns == []
    assert state.action_items == []
    assert state.error is None


def test_trade_record():
    t = TradeRecord(
        uuid="abc-123",
        market="KRW-BTC",
        side="buy",
        price=50000000,
        volume=0.01,
        funds=500000,
        fee=250,
        traded_at="2024-01-15T09:30:00",
    )
    assert t.market == "KRW-BTC"
    assert t.trade_type is None


def test_pattern_info():
    p = PatternInfo(
        pattern_type="FOMO_BUYING",
        description="상승장에서 충동 매수",
        frequency=12,
        severity="high",
        evidence=["1월 15일 BTC 급등 시 매수"],
    )
    assert p.severity == "high"
    assert len(p.evidence) == 1


def test_action_item():
    a = ActionItem(
        action="BTC 매수 시 -3% 손절라인 설정",
        priority="high",
        metric="다음 10건 거래 손절 설정 비율",
        timeframe="2주 후",
    )
    assert a.priority == "high"


def test_coin_summary():
    c = CoinSummary(
        market="KRW-BTC",
        trade_count=20,
        realized_pnl=150000,
        pnl_pct=3.5,
        avg_hold_hours=48.2,
    )
    assert c.pnl_pct == 3.5


def test_state_with_trades():
    trades = [
        TradeRecord(
            uuid=f"t-{i}",
            market="KRW-BTC",
            side="buy" if i % 2 == 0 else "sell",
            price=50000000,
            volume=0.01,
            funds=500000,
            fee=250,
            traded_at=f"2024-01-{15+i:02d}T10:00:00",
        )
        for i in range(10)
    ]
    state = CoachingState(trades=trades)
    assert len(state.trades) == 10


def test_pipeline_graph_compiles():
    """Verify LangGraph pipeline compiles without errors."""
    from app.agents.graph import coaching_pipeline
    assert coaching_pipeline is not None
