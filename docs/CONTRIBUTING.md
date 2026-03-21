# Contributing to bitcoach

Thanks for your interest in contributing!

## Getting Started

1. Fork and clone the repo
2. Copy `.env.example` to `.env` and add your `ANTHROPIC_API_KEY`
3. Run `docker compose up --build`
4. Frontend at http://localhost:5173, backend at http://localhost:8000

## Development Guidelines

### Backend (Python)
- Python 3.11+, type hints everywhere
- `ruff` for linting (`make backend-lint`)
- `pytest` for tests (`make backend-test`)
- Add tests for new features

### Frontend (TypeScript)
- React 18 with hooks
- Tailwind CSS for styling
- TanStack Query for server state
- `tsc --noEmit` for type checking

### Commit Convention
- `feat:` new feature
- `fix:` bug fix
- `docs:` documentation
- `refactor:` code restructuring
- `test:` adding tests

## Architecture Decisions

- **Backend proxy for Upbit API**: Upbit Exchange API requires fixed IP and doesn't support browser CORS. All API calls go through the FastAPI backend.
- **In-memory credential management**: API keys are never persisted. Session-based with automatic expiry.
- **LangGraph for AI pipeline**: State-based graph enables independent node testing and conditional branching.
- **SQLite for MVP**: Zero-config local database. PostgreSQL migration planned for v2.

## Need Help?

Open an issue or start a discussion!
