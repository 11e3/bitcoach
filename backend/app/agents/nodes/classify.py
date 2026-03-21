"""Node 1: Classify trades by type using Haiku (batch, low-cost).

Trade types:
- FOMO: Buying into a pump after significant price increase
- DIP_BUY: Buying after a dip
- SWING: Multi-day position with planned entry/exit
- SCALP: Very short hold (<1h)
- DCA: Dollar cost averaging (regular buys)
- PANIC_SELL: Selling at a loss quickly after buying
- TAKE_PROFIT: Selling at a gain
- STOP_LOSS: Selling at a planned loss level
- UNKNOWN: Cannot determine
"""

import json

from anthropic import AsyncAnthropic

from app.agents.state import CoachingState
from app.config import get_settings

CLASSIFY_PROMPT = """You are a crypto trade classifier. Classify each trade pair (buy→sell) into one of these types:
- FOMO: Bought after significant price pump
- DIP_BUY: Bought during a dip
- SWING: Held for days with planned entry/exit
- SCALP: Held for less than 1 hour
- DCA: Regular periodic buying pattern
- PANIC_SELL: Sold at loss very quickly after buying
- TAKE_PROFIT: Sold at a gain
- STOP_LOSS: Sold at a planned loss level
- AVERAGING_DOWN: Bought more of a losing position
- UNKNOWN: Cannot determine

Given these trades, classify each one. Consider:
- Time between buy and sell
- Whether it was profitable
- The pattern context (multiple buys of same coin, timing, etc.)

Trades:
{trades_json}

Respond with ONLY a JSON array of objects:
[{{"uuid": "...", "trade_type": "..."}}]

No explanation, just the JSON array."""


async def classify_trades(state: CoachingState) -> CoachingState:
    """Classify trades using Haiku for cost efficiency."""
    settings = get_settings()

    if not settings.anthropic_api_key or not state.trades:
        # Skip classification if no API key or no trades
        state.classified_trades = state.trades
        return state

    client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    # Prepare simplified trade data for LLM
    trade_data = []
    for t in state.trades[:200]:  # Limit to 200 for context window
        trade_data.append({
            "uuid": t.uuid,
            "market": t.market,
            "side": t.side,
            "price": t.price,
            "funds": round(t.funds),
            "traded_at": t.traded_at,
        })

    try:
        response = await client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=4096,
            messages=[{
                "role": "user",
                "content": CLASSIFY_PROMPT.format(trades_json=json.dumps(trade_data, ensure_ascii=False)),
            }],
        )

        result_text = response.content[0].text.strip()
        # Clean potential markdown
        if result_text.startswith("```"):
            result_text = result_text.split("\n", 1)[1].rsplit("```", 1)[0]

        classifications = json.loads(result_text)
        type_map = {c["uuid"]: c["trade_type"] for c in classifications}

        # Apply classifications
        classified = []
        type_counts: dict[str, int] = {}
        for trade in state.trades:
            trade.trade_type = type_map.get(trade.uuid, "UNKNOWN")
            classified.append(trade)
            type_counts[trade.trade_type] = type_counts.get(trade.trade_type, 0) + 1

        state.classified_trades = classified
        state.classification_summary = type_counts

    except Exception as e:
        # Graceful fallback — classification is enhancement, not critical
        state.classified_trades = state.trades
        state.error = f"Classification error: {str(e)}"

    return state
