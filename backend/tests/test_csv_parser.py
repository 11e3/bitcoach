"""Tests for CSV parser."""

import pytest

from app.core.csv_parser import parse_csv


SAMPLE_CSV = """종류,거래일시,마켓,거래금액,거래수량,거래단가,수수료,정산금액,주문유형
매수,2024-01-15 09:30:00,KRW-BTC,500000,0.01,50000000,250,500250,지정가
매도,2024-01-16 14:00:00,KRW-BTC,520000,0.01,52000000,260,519740,지정가
매수,2024-01-17 10:00:00,KRW-ETH,300000,0.1,3000000,150,300150,시장가
"""

SAMPLE_CSV_NO_MARKET = """종류,거래일시,코인,거래금액,거래수량,거래단가,수수료,정산금액,주문유형
매수,2024-01-15 09:30:00,BTC,500000,0.01,50000000,250,500250,지정가
매도,2024-01-16 14:00:00,BTC,520000,0.01,52000000,260,519740,지정가
"""

SAMPLE_CSV_WITH_COMMAS = """종류,거래일시,마켓,거래금액,거래수량,거래단가,수수료,정산금액,주문유형
매수,2024-01-15 09:30:00,KRW-BTC,"1,500,000",0.03,"50,000,000","750","1,500,750",지정가
"""


def test_parse_basic_csv():
    trades = parse_csv(SAMPLE_CSV)
    assert len(trades) == 3

    # First trade: buy BTC
    t = trades[0]
    assert t.market == "KRW-BTC"
    assert t.side == "buy"
    assert t.funds == 500000
    assert t.volume == 0.01
    assert t.fee == 250

    # Second: sell BTC
    t = trades[1]
    assert t.side == "sell"
    assert t.funds == 520000


def test_parse_csv_without_market_column():
    """When CSV has 'coin' column instead of 'market'."""
    trades = parse_csv(SAMPLE_CSV_NO_MARKET)
    assert len(trades) == 2
    assert trades[0].market == "KRW-BTC"
    assert trades[1].market == "KRW-BTC"


def test_parse_csv_with_comma_numbers():
    """Numbers with comma formatting (e.g., 1,500,000)."""
    trades = parse_csv(SAMPLE_CSV_WITH_COMMAS)
    assert len(trades) == 1
    assert trades[0].funds == 1500000
    assert trades[0].fee == 750


def test_parse_csv_bytes_utf8():
    """Parse bytes with UTF-8 encoding."""
    data = SAMPLE_CSV.encode("utf-8")
    trades = parse_csv(data)
    assert len(trades) == 3


def test_parse_csv_bytes_euckr():
    """Parse bytes with EUC-KR encoding."""
    data = SAMPLE_CSV.encode("euc-kr")
    trades = parse_csv(data)
    assert len(trades) == 3


def test_parse_empty_csv():
    with pytest.raises(ValueError, match="empty"):
        parse_csv("")


def test_parse_unrecognized_headers():
    csv = "Name,Date,Amount\nfoo,2024-01-01,100\n"
    with pytest.raises(ValueError, match="Unrecognized"):
        parse_csv(csv)


def test_parse_csv_skips_empty_rows():
    csv = SAMPLE_CSV + "\n\n\n"
    trades = parse_csv(csv)
    assert len(trades) == 3


def test_parse_csv_datetime_formats():
    """Test various datetime formats."""
    templates = [
        ("매수,2024-01-15 09:30:00,KRW-BTC,500000,0.01,50000000,250,500250,지정가", True),
        ("매수,2024/01/15 09:30:00,KRW-BTC,500000,0.01,50000000,250,500250,지정가", True),
        ("매수,2024.01.15 09:30:00,KRW-BTC,500000,0.01,50000000,250,500250,지정가", True),
    ]
    header = "종류,거래일시,마켓,거래금액,거래수량,거래단가,수수료,정산금액,주문유형\n"
    for row, should_parse in templates:
        trades = parse_csv(header + row)
        assert (len(trades) > 0) == should_parse, f"Failed for: {row}"
