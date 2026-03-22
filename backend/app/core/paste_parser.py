"""Parser for Upbit web copy-paste text.

Parses text copied from 업비트 웹 → 투자내역 → 거래내역 (Ctrl+A, Ctrl+C).
Handles mixed content (menus, headers, ads) by scanning for date patterns
and extracting 10-line trade blocks.

Each trade block (10 lines):
  1. 체결시간     2025.09.18 12:17
  2. 코인         XRP
  3. 마켓         KRW
  4. 종류         매수 / 매도 / 출금 / 입금
  5. 체결수량     1,173.69239540XRP
  6. 체결단가     4,312.0KRW
  7. 체결금액     5,060,962KRW
  8. 수수료       2,530.48KRW
  9. 정산금액     5,063,492KRW
  10. 주문시간    2025.09.18 12:17
"""

import re
import uuid
from dataclasses import dataclass
from datetime import datetime

# Date pattern: 2025.09.18 12:17 or 2025.09.18 09:00
DATE_RE = re.compile(r"^\d{4}\.\d{2}\.\d{2}\s+\d{2}:\d{2}$")
# Number with optional commas and trailing unit: 1,173.69239540XRP or 5,060,962KRW
NUM_RE = re.compile(r"^[\d,]+\.?\d*")


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


def _parse_number(s: str) -> float:
    """Parse '1,173.69239540XRP' → 1173.6924054."""
    m = NUM_RE.match(s.strip())
    if not m:
        return 0.0
    return float(m.group(0).replace(",", ""))


def _parse_datetime(s: str) -> datetime:
    """Parse '2025.09.18 12:17' → datetime."""
    return datetime.strptime(s.strip(), "%Y.%m.%d %H:%M")


def parse_paste(text: str) -> list[ParsedTrade]:
    """Parse pasted text from Upbit web trade history.

    Scans for date-pattern lines, then reads the next 9 lines as a trade block.
    Skips deposits/withdrawals (종류 = 출금/입금) and malformed blocks.
    """
    lines = [line.strip() for line in text.splitlines()]
    raw_trades: list[ParsedTrade] = []
    i = 0

    while i < len(lines):
        # Scan for a line matching date pattern (start of a trade block)
        if not DATE_RE.match(lines[i]):
            i += 1
            continue

        # Need 10 lines total for a complete block
        if i + 9 >= len(lines):
            break

        try:
            traded_at_str = lines[i]      # 체결시간
            coin = lines[i + 1]           # 코인 (XRP, BTC, ...)
            quote = lines[i + 2]          # 마켓 (KRW, BTC, ...)
            side_str = lines[i + 3]       # 종류 (매수/매도/출금/입금)
            volume_str = lines[i + 4]     # 체결수량
            price_str = lines[i + 5]      # 체결단가
            funds_str = lines[i + 6]      # 체결금액
            fee_str = lines[i + 7]        # 수수료
            # lines[i + 8]               # 정산금액 (skip)
            # lines[i + 9]               # 주문시간 (skip)

            # Skip deposits/withdrawals
            if side_str in ("출금", "입금"):
                i += 10
                continue

            # Skip if 마켓 is "-" (non-trade entry)
            if quote == "-":
                i += 10
                continue

            # Parse side
            if side_str == "매수":
                side = "buy"
            elif side_str == "매도":
                side = "sell"
            else:
                i += 1  # Not a valid trade, try next line
                continue

            # Build market code: KRW-XRP
            market = f"{quote}-{coin}"

            traded_at = _parse_datetime(traded_at_str)
            volume = _parse_number(volume_str)
            price = _parse_number(price_str)
            funds = _parse_number(funds_str)
            fee = _parse_number(fee_str)

            # Skip entries with zero amounts
            if funds <= 0 or volume <= 0:
                i += 10
                continue

            raw_trades.append(
                ParsedTrade(
                    uuid="",
                    market=market,
                    side=side,
                    price=price,
                    volume=volume,
                    funds=funds,
                    fee=fee,
                    traded_at=traded_at,
                )
            )
            i += 10

        except (ValueError, IndexError):
            # Malformed block, skip to next line and try again
            i += 1
            continue

    # --- Merge partial fills into single orders ---
    # Partial fills share the same (traded_at, market, side).
    merged: dict[tuple, ParsedTrade] = {}
    for t in raw_trades:
        key = (t.traded_at, t.market, t.side)
        if key in merged:
            m = merged[key]
            m.funds += t.funds
            m.volume += t.volume
            m.fee += t.fee
            # Recalculate weighted average price
            m.price = m.funds / m.volume if m.volume > 0 else 0
        else:
            merged[key] = ParsedTrade(
                uuid=str(uuid.uuid4()),
                market=t.market,
                side=t.side,
                price=t.price,
                volume=t.volume,
                funds=t.funds,
                fee=t.fee,
                traded_at=t.traded_at,
            )

    return list(merged.values())
