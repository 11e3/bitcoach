import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Float, Index, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TradeSide(StrEnum):
    BUY = "buy"
    SELL = "sell"


class Trade(Base):
    """Upbit spot trade record."""

    __tablename__ = "trades"

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[str] = mapped_column(String(64), index=True)
    session_id: Mapped[str] = mapped_column(String(64), index=True, default="")

    # Market info
    market: Mapped[str] = mapped_column(String(20), index=True)  # e.g. KRW-BTC
    side: Mapped[str] = mapped_column(String(4))  # buy / sell

    # Price & volume
    price: Mapped[float] = mapped_column(Float)
    volume: Mapped[float] = mapped_column(Float)
    funds: Mapped[float] = mapped_column(Float)  # price * volume
    fee: Mapped[float] = mapped_column(Float, default=0.0)

    # Timestamps
    traded_at: Mapped[datetime.datetime] = mapped_column(DateTime, index=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )

    # Classification (filled by LangGraph agent)
    trade_type: Mapped[str | None] = mapped_column(String(20), nullable=True)  # FOMO, swing, etc.

    __table_args__ = (
        Index("ix_trades_market_traded_at", "market", "traded_at"),
        Index("ix_trades_session_id", "session_id"),
    )
