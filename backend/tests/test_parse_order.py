"""Unit tests for _parse_order in trades route."""

from app.api.routes.trades import _parse_order


def test_limit_order():
    """Limit order: price is per-unit, funds = price * volume."""
    order = {
        "side": "bid",
        "ord_type": "limit",
        "price": "50000",
        "executed_volume": "10",
        "paid_fee": "250",
    }
    result = _parse_order(order)
    assert result["side"] == "buy"
    assert result["price"] == 50000.0
    assert result["volume"] == 10.0
    assert result["funds"] == 500000.0
    assert result["fee"] == 250.0


def test_market_sell_with_trades():
    """Market sell: price=null but trades field has fill details."""
    order = {
        "side": "ask",
        "ord_type": "market",
        "price": None,
        "executed_volume": "100",
        "paid_fee": "50",
        "trades": [
            {"price": "500", "volume": "60", "funds": "30000"},
            {"price": "510", "volume": "40", "funds": "20400"},
        ],
    }
    result = _parse_order(order)
    assert result["side"] == "sell"
    assert result["funds"] == 50400.0
    assert result["price"] == 504.0  # 50400 / 100
    assert result["volume"] == 100.0


def test_market_buy_with_trades():
    """Market buy (ord_type=price): trades field available."""
    order = {
        "side": "bid",
        "ord_type": "price",
        "price": "1000000",  # total KRW, NOT per-unit
        "executed_volume": "5.5",
        "paid_fee": "500",
        "trades": [
            {"price": "180000", "volume": "5.5", "funds": "990000"},
        ],
    }
    result = _parse_order(order)
    assert result["side"] == "buy"
    assert result["funds"] == 990000.0
    assert result["price"] == 990000.0 / 5.5


def test_executed_funds_fallback():
    """When trades is empty but executed_funds exists."""
    order = {
        "side": "ask",
        "ord_type": "market",
        "price": None,
        "executed_volume": "200",
        "executed_funds": "1000000",
        "paid_fee": "500",
    }
    result = _parse_order(order)
    assert result["funds"] == 1000000.0
    assert result["price"] == 5000.0


def test_no_price_no_trades_no_funds():
    """Market sell with no enrichment: funds=0 (will be skipped in sync)."""
    order = {
        "side": "ask",
        "ord_type": "market",
        "price": None,
        "executed_volume": "100",
        "paid_fee": "50",
    }
    result = _parse_order(order)
    assert result["funds"] == 0.0
    assert result["price"] == 0.0


def test_zero_volume():
    """Edge case: zero volume should not divide by zero."""
    order = {
        "side": "bid",
        "ord_type": "limit",
        "price": "50000",
        "executed_volume": "0",
        "paid_fee": "0",
    }
    result = _parse_order(order)
    assert result["funds"] == 0.0
    assert result["price"] == 50000.0


def test_trades_field_empty_list():
    """Empty trades list should fall through to other methods."""
    order = {
        "side": "bid",
        "ord_type": "limit",
        "price": "1000",
        "executed_volume": "5",
        "paid_fee": "2.5",
        "trades": [],
    }
    result = _parse_order(order)
    assert result["funds"] == 5000.0
