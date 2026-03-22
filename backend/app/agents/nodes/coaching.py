"""Node 4: Generate coaching report using Sonnet."""

import json

from anthropic import AsyncAnthropic

from app.agents.state import CoachingState
from app.config import get_settings

COACHING_PROMPT = """당신은 크립토 트레이딩 코치입니다. 아래 분석 데이터를 바탕으로 코칭 리포트를 작성하세요.

## 주의사항
- 특정 시간대(예: 9시 정각, 정시)에 반복되는 매매는 자동매매/봇 트레이딩일 가능성이 높습니다. 감정적 판단(공황 매매, 패닉 셀)으로 해석하지 마세요.
- 같은 시간대에 다수 체결이 몰려있으면 부분체결(하나의 주문이 여러 건으로 쪼개진 것)일 수 있습니다. 과거래로 판단하지 마세요.
- 실제 의사결정 횟수와 체결 건수는 다를 수 있습니다.

## 전체 통계
{stats_json}

## 종목별 성과 (상위 15)
{coin_json}

## 거래 분류 요약
{classification_json}

## 시간대 분석
{time_json}

## 발견된 패턴
{patterns_json}

---

아래 형식으로 코칭 리포트를 작성하세요. 각 섹션은 마크다운 없이 순수 텍스트로 작성합니다.

**톤**: 친근하지만 직설적. 숫자 근거를 반드시 포함. 빈말 금지. 자동매매 가능성을 고려하여 판단.

**중요**: 전체 통계의 realized_pnl이 정확한 실현 손익입니다. 종목별 손익을 합산할 때 이 숫자와 일치하는지 반드시 검증하세요. 자의적으로 재계산하지 마세요. 제공된 통계 수치를 그대로 인용하세요.

반드시 아래 JSON 형식으로만 응답하세요:

{{
  "summary": "전체 요약 (3-4문장. 핵심 수치 포함)",
  "strengths": "강점 분석 (2-3개 항목. 구체적 숫자 근거)",
  "weaknesses": "약점 분석 (2-3개 항목. 구체적 숫자 근거. 가장 중요한 것부터)",
  "suggestions": "개선 제안 (3-4개. 각각 구체적이고 실행 가능한 것)"
}}

JSON only."""


async def generate_coaching(state: CoachingState) -> CoachingState:
    """Generate coaching report using Sonnet."""
    settings = get_settings()

    if not settings.anthropic_api_key:
        state.report_summary = "API 키가 설정되지 않아 AI 코칭을 생성할 수 없습니다."
        return state

    client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    coin_data = [c.model_dump() for c in state.coin_performance[:15]]
    patterns_data = [p.model_dump() for p in state.patterns]

    try:
        response = await client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2048,
            messages=[{
                "role": "user",
                "content": COACHING_PROMPT.format(
                    stats_json=json.dumps(state.overall_stats, ensure_ascii=False),
                    coin_json=json.dumps(coin_data, ensure_ascii=False),
                    classification_json=json.dumps(state.classification_summary, ensure_ascii=False),
                    time_json=json.dumps(state.time_analysis, ensure_ascii=False),
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
