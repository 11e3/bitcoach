<div align="center">

# bitcoach

**업비트 현물 거래내역을 AI가 분석해서 트레이딩 습관 개선점을 코칭해주는 오픈소스 도구**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB.svg)](https://python.org)
[![React 18](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agentic-green.svg)](https://langchain-ai.github.io/langgraph/)

</div>

---

## What it does

1. **업비트 거래내역 가져오기** — API Key 또는 CSV 업로드
2. **통계 분석** — 승률, 종목별 PnL, 시간대/요일 분포, 보유기간, FIFO 매매 매칭
3. **AI 코칭** — LangGraph 5단계 파이프라인이 반복 패턴을 찾아 실행 가능한 개선안 제안

## Pipeline

```
① classify (Haiku)   — 거래 유형 자동 분류 (FOMO, 손절, 스윙 등)
② statistics (Python) — FIFO 매칭, 승률, PnL, 보유기간 계산
③ patterns (Haiku)    — 반복 행동 패턴 탐지
④ coaching (Sonnet)   — 강점/약점/개선안 종합 리포트
⑤ actions (Sonnet)    — 측정 가능한 실행 액션 아이템 추출
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

## Tech Stack

| Layer | Tech |
|-------|------|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, Recharts, TanStack Query |
| Backend | FastAPI, Python 3.11+, SQLAlchemy (async), SQLite |
| AI Pipeline | LangGraph, Claude API (Sonnet + Haiku), Anthropic SDK |
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
             Haiku API     Python Compute  Sonnet API
            (classify,     (statistics)   (coaching,
             patterns)                     actions)
                                │
                            SQLite DB
```

**Security**: API Keys → server memory only → never persisted to disk/DB → auto-cleared on restart. Backend proxies Upbit API calls (Upbit Exchange API requires fixed IP, no browser CORS support).

## Data Input

| Method | Pros | Cons |
|--------|------|------|
| **API Key** | Auto-sync, real-time | Fixed IP required |
| **CSV Upload** | No API key needed, zero barrier | Manual updates |

### API Key Setup

1. 업비트 → Open API 관리 → 새 키 발급
2. **출금 권한 OFF** (조회 전용)
3. 허용 IP에 서버 공인 IP 등록
4. bitcoach 설정 페이지에서 Access Key + Secret Key 입력

## Development

```bash
# Run with hot-reload
make dev

# Backend tests
make backend-test

# Backend lint
make backend-lint

# Logs
make logs

# Clean everything
make clean
```

### Project Structure

```
bitcoach/
├── frontend/          React 18 + TypeScript + Tailwind
│   └── src/
│       ├── pages/     Landing, Setup, Dashboard, Coaching
│       ├── components/ Layout, charts, UI components
│       └── lib/       API client, utilities
│
├── backend/           FastAPI + Python 3.11+
│   └── app/
│       ├── agents/    LangGraph pipeline
│       │   ├── graph.py       Pipeline definition
│       │   ├── state.py       Shared state
│       │   └── nodes/         5 pipeline nodes
│       ├── api/routes/        REST endpoints
│       ├── core/              Upbit client, CSV parser, security
│       ├── services/          Trade analyzer, coaching orchestrator
│       └── models/            SQLAlchemy models
│
└── docker-compose.yml  One-command setup
```

## API Endpoints

### Trades
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/trades/connect` | Submit API keys (memory only) |
| POST | `/api/trades/sync` | Fetch trades from Upbit |
| POST | `/api/trades/upload-csv` | Upload CSV file |
| POST | `/api/trades/disconnect` | Clear keys from memory |
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
| GET | `/api/coaching/reports` | List reports |
| GET | `/api/coaching/reports/:id` | Report detail |

## License

MIT

## Contributing

PRs welcome! See [CONTRIBUTING.md](docs/CONTRIBUTING.md).

1. Fork the repo
2. Create a feature branch (`git checkout -b feat/amazing-feature`)
3. Commit (`git commit -m 'Add amazing feature'`)
4. Push (`git push origin feat/amazing-feature`)
5. Open a Pull Request
