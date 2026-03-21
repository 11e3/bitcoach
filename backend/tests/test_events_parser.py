"""Tests for Upbit events API JSON parser."""

import json

from app.core.events_parser import parse_events

SAMPLE_EVENTS = [
    {
        "uuid": "df08d347-2833-40d9-8868-9ad020999ca7",
        "event_type": "bid",
        "market": "KRW-XRP",
        "price": "3989",
        "volume": "300",
        "amount": "1196700",
        "fee": "598.35",
        "event_at": "2025-09-03T09:27:48+09:00",
        "transaction_type": "default",
    },
    {
        "uuid": "41901a47-23f0-4823-bb8c-0c1df3d91883",
        "event_type": "ask",
        "market": "KRW-XRP",
        "price": "4271",
        "volume": "117.06860221",
        "amount": "500000",
        "fee": "250",
        "event_at": "2025-09-18T09:00:00+09:00",
        "transaction_type": "default",
    },
]


def test_parse_events_basic():
    text = json.dumps(SAMPLE_EVENTS)
    trades = parse_events(text)
    assert len(trades) == 2

    t0 = trades[0]
    assert t0.side == "buy"
    assert t0.market == "KRW-XRP"
    assert t0.price == 3989.0
    assert t0.volume == 300.0
    assert t0.funds == 1196700.0
    assert t0.fee == 598.35
    assert t0.uuid == "df08d347-2833-40d9-8868-9ad020999ca7"

    t1 = trades[1]
    assert t1.side == "sell"
    assert t1.funds == 500000.0


def test_parse_events_filters_non_trades():
    events = SAMPLE_EVENTS + [
        {
            "uuid": "deposit-1",
            "event_type": "deposit",
            "market": "KRW",
            "price": "1",
            "volume": "1000000",
            "amount": "1000000",
            "fee": "0",
            "event_at": "2025-01-01T00:00:00+09:00",
        },
        {
            "uuid": "withdraw-1",
            "event_type": "withdraw",
            "market": "KRW",
            "price": "1",
            "volume": "500000",
            "amount": "500000",
            "fee": "1000",
            "event_at": "2025-01-02T00:00:00+09:00",
        },
    ]
    trades = parse_events(json.dumps(events))
    assert len(trades) == 2  # only bid and ask


def test_parse_events_empty():
    assert parse_events("[]") == []


def test_parse_events_invalid_json():
    import pytest
    with pytest.raises(Exception):
        parse_events("not json")
