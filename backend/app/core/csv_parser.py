"""Parser for Upbit trade history CSV exports.

Upbit CSV format (Korean headers):
종류,거래일시,거래금액,거래수량,거래단가,수수료,정산금액,주문유형
"""

import csv
import io
import uuid
from datetime import datetime

from pydantic import BaseModel


class ParsedTrade(BaseModel):
    """Normalized trade record from CSV."""

    uuid: str  # Generated if not in CSV
    market: str
    side: str  # "buy" or "sell"
    price: float
    volume: float
    funds: float
    fee: float
    traded_at: datetime


# Known Upbit CSV header mappings (Korean → field)
HEADER_MAP = {
    "종류": "side",
    "거래일시": "traded_at",
    "마켓": "market",
    "거래금액": "funds",
    "거래수량": "volume",
    "거래단가": "price",
    "수수료": "fee",
    "정산금액": "settlement",
    "주문유형": "order_type",
    "코인": "coin",
}

SIDE_MAP = {
    "매수": "buy",
    "매도": "sell",
    "bid": "buy",
    "ask": "sell",
}


def _parse_datetime(value: str) -> datetime:
    """Parse various datetime formats from Upbit CSV."""
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%Y.%m.%d %H:%M:%S",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(value.strip(), fmt)
        except ValueError:
            continue
    raise ValueError(f"Unable to parse datetime: {value}")


def _parse_number(value: str) -> float:
    """Parse number string, handling Korean formatting (commas, etc)."""
    cleaned = value.strip().replace(",", "").replace(" ", "")
    if not cleaned or cleaned == "-":
        return 0.0
    return float(cleaned)


def _normalize_headers(headers: list[str]) -> dict[int, str]:
    """Map CSV column indices to our field names."""
    mapping: dict[int, str] = {}
    for i, header in enumerate(headers):
        clean = header.strip().replace("\ufeff", "")  # Remove BOM
        if clean in HEADER_MAP:
            mapping[i] = HEADER_MAP[clean]
    return mapping


def parse_csv(content: str | bytes) -> list[ParsedTrade]:
    """Parse Upbit trade history CSV content.

    Args:
        content: CSV file content as string or bytes

    Returns:
        List of parsed trade records

    Raises:
        ValueError: If CSV format is unrecognized
    """
    if isinstance(content, bytes):
        # Try UTF-8 first, then EUC-KR (common Korean encoding)
        for encoding in ["utf-8-sig", "utf-8", "euc-kr", "cp949"]:
            try:
                content = content.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        else:
            raise ValueError("Unable to decode CSV file. Supported encodings: UTF-8, EUC-KR")

    reader = csv.reader(io.StringIO(content))
    headers = next(reader, None)

    if headers is None:
        raise ValueError("CSV file is empty")

    col_map = _normalize_headers(headers)

    if not col_map:
        raise ValueError(
            f"Unrecognized CSV headers: {headers}. "
            "Expected Upbit trade history format with Korean headers."
        )

    trades: list[ParsedTrade] = []

    for row_num, row in enumerate(reader, start=2):
        if not row or all(cell.strip() == "" for cell in row):
            continue

        try:
            record: dict = {}
            for col_idx, field_name in col_map.items():
                if col_idx < len(row):
                    record[field_name] = row[col_idx]

            # Parse side
            raw_side = record.get("side", "")
            side = SIDE_MAP.get(raw_side.strip(), raw_side.strip().lower())
            if side not in ("buy", "sell"):
                continue  # Skip unknown trade types

            # Parse numbers
            price = _parse_number(record.get("price", "0"))
            volume = _parse_number(record.get("volume", "0"))
            funds = _parse_number(record.get("funds", "0"))
            fee = _parse_number(record.get("fee", "0"))

            # Calculate funds if missing
            if funds == 0 and price > 0 and volume > 0:
                funds = price * volume

            # Parse datetime
            traded_at = _parse_datetime(record.get("traded_at", ""))

            # Build market code
            market = record.get("market", "")
            if not market and "coin" in record:
                market = f"KRW-{record['coin'].strip().upper()}"

            trades.append(
                ParsedTrade(
                    uuid=str(uuid.uuid4()),
                    market=market,
                    side=side,
                    price=price,
                    volume=volume,
                    funds=funds,
                    fee=fee,
                    traded_at=traded_at,
                )
            )

        except (ValueError, KeyError, IndexError) as e:
            # Skip malformed rows but continue parsing
            continue

    return trades
