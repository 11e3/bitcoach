"""Parser for Upbit internal events API JSON.

Parses the output of the browser console script that calls
ccx.upbit.com/api/v1/investments/events.

Each event has:
  uuid, event_type (bid/ask), market, price, volume, amount (=funds),
  fee, event_at, transaction_type
"""

import json
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ParsedTrade:
    uuid: str
    market: str
    side: str
    price: float
    volume: float
    funds: float
    fee: float
    traded_at: datetime


def parse_events(text: str) -> list[ParsedTrade]:
    """Parse JSON array of events from Upbit internal API.

    Filters to only bid/ask events (excludes deposits, withdrawals, etc).
    """
    data = json.loads(text)
    if not isinstance(data, list):
        raise ValueError("JSON 배열이 아닙니다.")

    trades: list[ParsedTrade] = []
    for event in data:
        event_type = event.get("event_type", "")
        if event_type not in ("bid", "ask"):
            continue

        side = "buy" if event_type == "bid" else "sell"
        try:
            traded_at = datetime.fromisoformat(event["event_at"])
        except (KeyError, ValueError):
            continue

        trades.append(
            ParsedTrade(
                uuid=event.get("uuid", ""),
                market=event.get("market", ""),
                side=side,
                price=float(event.get("price", 0) or 0),
                volume=float(event.get("volume", 0) or 0),
                funds=float(event.get("amount", 0) or 0),
                fee=float(event.get("fee", 0) or 0),
                traded_at=traded_at,
            )
        )

    return trades
