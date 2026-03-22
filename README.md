<div align="center">

# bitcoach

**업비트 거래내역을 AI가 분석해서 트레이딩 습관 개선점을 코칭해주는 오픈소스 도구**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB.svg)](https://python.org)
[![React 18](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agentic-green.svg)](https://langchain-ai.github.io/langgraph/)

</div>

---

## What it does

1. **거래내역 가져오기** — 업비트 웹에서 복사-붙여넣기 (부분체결 자동 합산, 입출금 자동 제외)
2. **통계 분석** — 승률, 종목별 PnL, 시간대/요일 분포, 보유기간, FIFO 매매 매칭
3. **AI 코칭** — LangGraph 5단계 파이프라인이 반복 패턴을 찾아 실행 가능한 개선안 제안

## Pipeline

```
① classify (Haiku)   — 거래 유형 자동 분류 (FOMO, 손절, 스윙 등)
② statistics (Python) — FIFO 매칭, 승률, PnL, 보유기간 계산
③ patterns (Haiku)    — 반복 행동 패턴 탐지
④ coaching (Haiku)    — 강점/약점/개선안 종합 리포트
⑤ actions (Haiku)     — 측정 가능한 실행 액션 아이템 추출
```

## Quick Start

```bash
git clone https://github.com/11e3/bitcoach.git
cd bitcoach
cp .env.example .env
# .env에 ANTHROPIC_API_KEY 입력

docker compose up --build
```

- Frontend: http://localhost:5173
- Backend API docs: http://localhost:8000/docs

## Data Input

업비트 웹 → 투자내역 → 거래내역에서 드래그 복사 → bitcoach 설정 페이지에 붙여넣기.

- 메뉴/헤더 등이 함께 복사되어도 거래내역만 자동 추출
- 부분체결은 같은 주문으로 자동 합산
- 입출금 기록 자동 제외

## Tech Stack

| Layer | Tech |
|-------|------|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, Recharts, TanStack Query |
| Backend | FastAPI, Python 3.11+, SQLAlchemy (async), SQLite |
| AI Pipeline | LangGraph, Claude Haiku API, LangChain-Anthropic |
| Infra | Docker Compose, GitHub Actions CI |

## Architecture

```
React Frontend ──REST API──▶ FastAPI Backend
                                │
                        ┌───────┴───────┐
                        │ LangGraph     │
                        │ 5-node agent  │
                        └───────┬───────┘
                                │
                  ┌─────────────┼─────────────┐
                  ▼             ▼             ▼
             Haiku API     Python Compute  Haiku API
            (classify,     (statistics)   (coaching,
             patterns)                     actions)
                                │
                            SQLite DB
```

## API Endpoints

### Trades
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/trades/paste` | Import trades from copy-paste |
| GET | `/api/trades` | List trades (filterable) |
| GET | `/api/trades/statistics` | Basic stats |

### Analysis
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/analysis/full` | Complete analysis (all charts) |
| GET | `/api/analysis/by-coin` | Per-coin performance |
| GET | `/api/analysis/by-time` | Hourly distribution |

### Coaching
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/coaching/generate` | Run LangGraph pipeline |

## Development

```bash
make dev            # Run with hot-reload
make backend-test   # Backend tests
make backend-lint   # Backend lint
make logs           # Logs
make clean          # Clean everything
```

### Project Structure

```
bitcoach/
├── frontend/          React 18 + TypeScript + Tailwind
│   └── src/
│       ├── pages/     Landing, Setup, Dashboard, Coaching
│       ├── components/ Layout, charts, UI
│       └── lib/       API client, utilities
│
├── backend/           FastAPI + Python 3.11+
│   └── app/
│       ├── agents/    LangGraph pipeline
│       │   ├── graph.py       Pipeline definition
│       │   ├── state.py       Shared state
│       │   └── nodes/         5 pipeline nodes
│       ├── api/routes/        REST endpoints
│       ├── core/              Paste parser, security
│       ├── services/          Trade analyzer, coaching orchestrator
│       └── models/            SQLAlchemy models
│
└── docker-compose.yml  One-command setup
```

## Disclaimer

본 서비스는 투자 자문이 아닙니다. AI가 제공하는 분석과 코칭은 참고 자료일 뿐이며, 투자 결정에 대한 책임은 전적으로 이용자에게 있습니다. 과거 거래 분석 결과가 미래 수익을 보장하지 않습니다.

## License

MIT

## Contributing

PRs welcome! See [CONTRIBUTING.md](docs/CONTRIBUTING.md).
