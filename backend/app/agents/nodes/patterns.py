"""Node 3: Detect recurring trade patterns using Haiku."""

import json

from anthropic import AsyncAnthropic

from app.agents.state import CoachingState, PatternInfo
from app.config import get_settings

PATTERNS_PROMPT = """You are a crypto trading pattern detector. Analyze these trading statistics and classified trades to find recurring behavioral patterns — especially bad habits.

## Trading Statistics
{stats_json}

## Coin Performance
{coin_json}

## Time Analysis
{time_json}

## Trade Classification Summary
{classification_json}

## Recent Trades (sample)
{trades_sample}

Identify 3-7 behavioral patterns. Focus on:
1. Timing patterns: Do they trade at bad times? Overactive on certain days?
2. Loss patterns: FOMO buying, panic selling, averaging down on losers
3. Position sizing: Concentration risk, too many small trades
4. Holding patterns: Too short (scalping losses) or too long (hope trading)
5. Win/loss asymmetry: Small wins, big losses?

Respond with ONLY a JSON array:
[{{
  "pattern_type": "FOMO_BUYING",
  "description": "설명 (한국어)",
  "frequency": 12,
  "severity": "high",
  "evidence": ["구체적 증거 1", "구체적 증거 2"]
}}]

한국어로 작성. JSON only, no explanation."""


async def detect_patterns(state: CoachingState) -> CoachingState:
    """Detect behavioral patterns using Haiku."""
    settings = get_settings()

    if not settings.anthropic_api_key:
        return state

    client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    # Prepare context
    trades_sample = []
    for t in state.classified_trades[:50]:
        trades_sample.append({
            "market": t.market,
            "side": t.side,
            "funds": round(t.funds),
            "traded_at": t.traded_at,
            "type": t.trade_type,
        })

    coin_data = [c.model_dump() for c in state.coin_performance[:15]]

    try:
        response = await client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2048,
            messages=[{
                "role": "user",
                "content": PATTERNS_PROMPT.format(
                    stats_json=json.dumps(state.overall_stats, ensure_ascii=False),
                    coin_json=json.dumps(coin_data, ensure_ascii=False),
                    time_json=json.dumps(state.time_analysis, ensure_ascii=False),
                    classification_json=json.dumps(state.classification_summary, ensure_ascii=False),
                    trades_sample=json.dumps(trades_sample, ensure_ascii=False),
                ),
            }],
        )

        result_text = response.content[0].text.strip()
        if result_text.startswith("```"):
            result_text = result_text.split("\n", 1)[1].rsplit("```", 1)[0]

        patterns_raw = json.loads(result_text)
        state.patterns = [PatternInfo(**p) for p in patterns_raw]

    except Exception as e:
        state.patterns = []
        if not state.error:
            state.error = f"Pattern detection error: {str(e)}"

    return state
