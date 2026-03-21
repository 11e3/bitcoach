"""API health and basic endpoint tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "0.1.0"


@pytest.mark.asyncio
async def test_get_trades_empty(client: AsyncClient):
    response = await client.get("/api/trades")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_statistics_empty(client: AsyncClient):
    response = await client.get("/api/trades/statistics")
    assert response.status_code == 200
    data = response.json()
    assert data["total_trades"] == 0


@pytest.mark.asyncio
async def test_full_analysis_empty(client: AsyncClient):
    response = await client.get("/api/analysis/full")
    assert response.status_code == 200
    data = response.json()
    assert data["overall"]["total_trades"] == 0


@pytest.mark.asyncio
async def test_coaching_reports_empty(client: AsyncClient):
    response = await client.get("/api/coaching/reports")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_coaching_report_not_found(client: AsyncClient):
    response = await client.get("/api/coaching/reports/999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_upload_csv_wrong_type(client: AsyncClient):
    import io
    response = await client.post(
        "/api/trades/upload-csv",
        files={"file": ("data.txt", io.BytesIO(b"hello"), "text/plain")},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_upload_csv_valid(client: AsyncClient):
    csv_content = (
        "종류,거래일시,마켓,거래금액,거래수량,거래단가,수수료,정산금액,주문유형\n"
        "매수,2024-01-15 09:30:00,KRW-BTC,500000,0.01,50000000,250,500250,지정가\n"
        "매도,2024-01-16 14:00:00,KRW-BTC,520000,0.01,52000000,260,519740,지정가\n"
    )
    import io
    response = await client.post(
        "/api/trades/upload-csv",
        files={"file": ("trades.csv", io.BytesIO(csv_content.encode()), "text/csv")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["synced"] == 2

    # Verify trades are in DB
    trades_resp = await client.get("/api/trades")
    assert len(trades_resp.json()) == 2

    # Verify statistics
    stats_resp = await client.get("/api/trades/statistics")
    stats = stats_resp.json()
    assert stats["total_trades"] == 2
    assert stats["total_buy"] == 1
    assert stats["total_sell"] == 1


@pytest.mark.asyncio
async def test_paste_events_json(client: AsyncClient):
    import json
    events = [
        {
            "uuid": "test-buy-1",
            "event_type": "bid",
            "market": "KRW-XRP",
            "price": "3989",
            "volume": "300",
            "amount": "1196700",
            "fee": "598.35",
            "event_at": "2025-09-03T09:27:48+09:00",
        },
        {
            "uuid": "test-sell-1",
            "event_type": "ask",
            "market": "KRW-XRP",
            "price": "4271",
            "volume": "117",
            "amount": "500000",
            "fee": "250",
            "event_at": "2025-09-18T09:00:00+09:00",
        },
        {
            "uuid": "test-deposit",
            "event_type": "deposit",
            "market": "KRW",
            "price": "1",
            "volume": "1000000",
            "amount": "1000000",
            "fee": "0",
            "event_at": "2025-01-01T00:00:00+09:00",
        },
    ]
    response = await client.post(
        "/api/trades/paste",
        json={"text": json.dumps(events)},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["synced"] == 2  # deposit filtered out
    assert data["total_parsed"] == 2

    trades_resp = await client.get("/api/trades")
    trades = trades_resp.json()
    assert len(trades) == 2

    buy = next(t for t in trades if t["side"] == "buy")
    assert buy["market"] == "KRW-XRP"
    assert buy["price"] == 3989.0
    assert buy["funds"] == 1196700.0


@pytest.mark.asyncio
async def test_paste_empty(client: AsyncClient):
    response = await client.post("/api/trades/paste", json={"text": "[]"})
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_sync_without_session(client: AsyncClient):
    response = await client.post("/api/trades/sync")
    assert response.status_code == 401
