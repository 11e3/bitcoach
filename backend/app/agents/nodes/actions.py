"""Node 5: Extract concrete action items from coaching report."""

import json

from anthropic import AsyncAnthropic

from app.agents.state import ActionItem, CoachingState
from app.config import get_settings

ACTIONS_PROMPT = """아래 코칭 리포트에서 구체적인 실행 가능한 액션 아이템을 추출하세요.

## 코칭 요약
{summary}

## 약점
{weaknesses}

## 개선 제안
{suggestions}

## 발견된 패턴
{patterns_json}

---

3-5개의 액션 아이템을 추출하세요. 각 액션은:
- 즉시 실행 가능해야 합니다
- 성공 여부를 측정할 수 있어야 합니다
- 구체적인 숫자 기준이 있어야 합니다

JSON 배열로만 응답:
[{{
  "action": "구체적 액션 (예: BTC 매수 시 반드시 -3% 손절라인 설정)",
  "priority": "high",
  "metric": "측정 방법 (예: 다음 10건 거래에서 손절라인 설정 비율)",
  "timeframe": "측정 시점 (예: 2주 후)"
}}]

JSON only."""


async def extract_actions(state: CoachingState) -> CoachingState:
    """Extract action items using Sonnet."""
    settings = get_settings()

    if not settings.anthropic_api_key or not state.report_summary:
        return state

    client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    patterns_data = [p.model_dump() for p in state.patterns]

    try:
        response = await client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": ACTIONS_PROMPT.format(
                    summary=state.report_summary,
                    weaknesses=state.report_weaknesses,
                    suggestions=state.report_suggestions,
                    patterns_json=json.dumps(patterns_data, ensure_ascii=False),
                ),
            }],
        )

        result_text = response.content[0].text.strip()
        if result_text.startswith("```"):
            result_text = result_text.split("\n", 1)[1].rsplit("```", 1)[0]

        actions_raw = json.loads(result_text)
        state.action_items = [ActionItem(**a) for a in actions_raw]

    except Exception as e:
        state.action_items = []
        if not state.error:
            state.error = f"Action extraction error: {str(e)}"

    return state
