"""Node 4: Generate coaching report using Haiku.

Numbers come from Python (precomputed_summary). Haiku only does qualitative analysis.
"""

import json

from anthropic import AsyncAnthropic

from app.agents.state import CoachingState
from app.config import get_settings

COACHING_PROMPT = """당신은 크립토 트레이딩 코치입니다.

## 규칙
1. 아래 "팩트 요약"의 숫자는 Python이 계산한 정확한 값입니다. 절대 수정하거나 재계산하지 마세요.
2. 숫자를 인용할 때 팩트 요약에 있는 값을 그대로 사용하세요.
3. 정시(9시, 18시 등)에 반복되는 매매는 자동매매/봇일 가능성이 높습니다. 감정적 판단으로 해석하지 마세요.
4. 같은 시간에 다수 체결은 부분체결(하나의 주문)입니다. 과거래로 판단하지 마세요.

{precomputed_summary}

## 거래 분류 요약
{classification_json}

## 발견된 패턴
{patterns_json}

---

위 데이터를 바탕으로 코칭 리포트를 작성하세요.

**톤**: 친근하지만 직설적. 팩트 요약의 숫자를 그대로 인용. 빈말 금지.

반드시 아래 JSON 형식으로만 응답하세요:

{{
  "summary": "전체 요약 (3-4문장. 팩트 요약의 수치를 그대로 인용)",
  "strengths": "강점 분석 (2-3개. 구체적 숫자 근거)",
  "weaknesses": "약점 분석 (2-3개. 구체적 숫자 근거. 가장 중요한 것부터)",
  "suggestions": "개선 제안 (3-4개. 각각 구체적이고 실행 가능한 것)"
}}

JSON only."""


async def generate_coaching(state: CoachingState) -> CoachingState:
    """Generate coaching report using Haiku with pre-computed factual summary."""
    settings = get_settings()

    if not settings.anthropic_api_key:
        state.report_summary = "API 키가 설정되지 않아 AI 코칭을 생성할 수 없습니다."
        return state

    client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    patterns_data = [p.model_dump() for p in state.patterns]

    try:
        response = await client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2048,
            messages=[{
                "role": "user",
                "content": COACHING_PROMPT.format(
                    precomputed_summary=state.precomputed_summary,
                    classification_json=json.dumps(state.classification_summary, ensure_ascii=False),
                    patterns_json=json.dumps(patterns_data, ensure_ascii=False),
                ),
            }],
        )

        result_text = response.content[0].text.strip()
        if result_text.startswith("```"):
            result_text = result_text.split("\n", 1)[1].rsplit("```", 1)[0]

        report = json.loads(result_text)

        state.report_summary = report.get("summary", "")
        state.report_strengths = report.get("strengths", "")
        state.report_weaknesses = report.get("weaknesses", "")
        state.report_suggestions = report.get("suggestions", "")

    except Exception as e:
        state.report_summary = f"코칭 리포트 생성 중 오류: {str(e)}"

    return state
