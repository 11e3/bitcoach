"""Tests for paste_parser — Upbit web copy-paste format."""
from app.core.paste_parser import ParsedTrade, _parse_number, parse_paste


SAMPLE_TWO_TRADES = """\
2025.09.18 12:17
XRP
KRW
매수
1,173.69239540XRP
4,312.0KRW
5,060,962KRW
2,530.48KRW
5,063,492KRW
2025.09.18 12:17
2025.09.18 09:00
XRP
KRW
매도
117.06860221XRP
4,271.0KRW
500,000KRW
250.00KRW
499,750KRW
2025.09.18 09:00
"""


def test_parse_two_trades():
    result = parse_paste(SAMPLE_TWO_TRADES)
    assert len(result) == 2

    buy = result[0]
    assert buy.side == "buy"
    assert buy.market == "KRW-XRP"
    assert abs(buy.price - 4312.0) < 0.01
    assert abs(buy.volume - 1173.6924) < 0.01
    assert abs(buy.funds - 5060962) < 1
    assert abs(buy.fee - 2530.48) < 0.01

    sell = result[1]
    assert sell.side == "sell"
    assert sell.market == "KRW-XRP"
    assert abs(sell.volume - 117.0686) < 0.01


def test_parse_number():
    assert _parse_number("1,173.69239540XRP") == 1173.6923954
    assert _parse_number("5,060,962KRW") == 5060962.0
    assert _parse_number("4,312.0KRW") == 4312.0
    assert _parse_number("0.00210000BTC") == 0.0021
    assert _parse_number("105,322,000KRW") == 105322000.0


def test_skip_deposits():
    text = """\
2026.03.17 08:05
KRW
-
출금
63,153KRW
1.000KRW
63,153KRW
1,000.00KRW
64,153KRW
-
2025.09.18 12:17
XRP
KRW
매수
1,173.69239540XRP
4,312.0KRW
5,060,962KRW
2,530.48KRW
5,063,492KRW
2025.09.18 12:17
"""
    result = parse_paste(text)
    assert len(result) == 1
    assert result[0].side == "buy"


def test_mixed_junk():
    text = """\
업비트 투자내역
로그인 상태입니다
메뉴 바 텍스트
2025.09.18 12:17
XRP
KRW
매수
1,173.69239540XRP
4,312.0KRW
5,060,962KRW
2,530.48KRW
5,063,492KRW
2025.09.18 12:17
더 많은 메뉴 텍스트
광고 배너 텍스트
"""
    result = parse_paste(text)
    assert len(result) == 1
    assert result[0].market == "KRW-XRP"


def test_empty_text():
    assert parse_paste("") == []
    assert parse_paste("no trades here") == []


def test_merge_partial_fills():
    """3 partial fills at same time → merged into 1 order."""
    text = """\
2025.12.20 14:33
XRP
KRW
매수
100.00000000XRP
2,855.0KRW
285,500KRW
142.75KRW
285,643KRW
2025.12.20 14:33
2025.12.20 14:33
XRP
KRW
매수
50.00000000XRP
2,855.0KRW
142,750KRW
71.37KRW
142,822KRW
2025.12.20 14:33
2025.12.20 14:33
XRP
KRW
매수
200.00000000XRP
2,855.0KRW
571,000KRW
285.50KRW
571,286KRW
2025.12.20 14:33
"""
    result = parse_paste(text)
    assert len(result) == 1
    assert result[0].market == "KRW-XRP"
    assert result[0].side == "buy"
    assert abs(result[0].volume - 350.0) < 0.01
    assert abs(result[0].funds - 999250.0) < 1
    assert abs(result[0].fee - 499.62) < 0.01
    assert abs(result[0].price - 999250.0 / 350.0) < 0.1


def test_btc_trade():
    text = """\
2026.03.08 19:17
BTC
KRW
매도
0.06776995BTC
100,384,000KRW
6,803,018KRW
3,401.50KRW
6,799,617KRW
2026.03.08 19:17
"""
    result = parse_paste(text)
    assert len(result) == 1
    assert result[0].market == "KRW-BTC"
    assert result[0].side == "sell"
    assert abs(result[0].price - 100384000) < 1
    assert abs(result[0].volume - 0.06776995) < 0.0000001
    assert abs(result[0].funds - 6803018) < 1
