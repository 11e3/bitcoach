"""LangGraph state definition for the coaching pipeline.

State flows through: classify → statistics → patterns → coaching → actions
"""

from typing import Any

from pydantic import BaseModel, Field


class TradeRecord(BaseModel):
    """Simplified trade record for agent context."""

    uuid: str
    market: str
    side: str
    price: float
    volume: float
    funds: float
    fee: float
    traded_at: str
    trade_type: str | None = None


class CoinSummary(BaseModel):
    market: str
    trade_count: int
    realized_pnl: float
    pnl_pct: float
    avg_hold_hours: float | None = None


class PatternInfo(BaseModel):
    pattern_type: str  # e.g., "FOMO_MORNING", "LOSS_CHASING", "OVERTRADING"
    description: str
    frequency: int
    severity: str  # "low", "medium", "high"
    evidence: list[str]


class ActionItem(BaseModel):
    action: str
    priority: str  # "high", "medium", "low"
    metric: str  # How to measure success
    timeframe: str  # When to check


class CoachingState(BaseModel):
    """Full state passed through the LangGraph pipeline."""

    # Input
    trades: list[TradeRecord] = Field(default_factory=list)

    # Step 1: Classification
    classified_trades: list[TradeRecord] = Field(default_factory=list)
    classification_summary: dict[str, int] = Field(default_factory=dict)

    # Step 2: Statistics (computed in Python)
    overall_stats: dict[str, Any] = Field(default_factory=dict)
    coin_performance: list[CoinSummary] = Field(default_factory=list)
    time_analysis: dict[str, Any] = Field(default_factory=dict)
    precomputed_summary: str = ""  # Python-generated factual summary for LLM

    # Step 3: Patterns
    patterns: list[PatternInfo] = Field(default_factory=list)

    # Step 4: Coaching report
    report_summary: str = ""
    report_strengths: str = ""
    report_weaknesses: str = ""
    report_suggestions: str = ""

    # Step 5: Action items
    action_items: list[ActionItem] = Field(default_factory=list)

    # Metadata
    error: str | None = None
