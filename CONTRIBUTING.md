# Contributing

Thanks for your interest in LOLTopNews! Here's how to get started.

## Development Setup

### Backend

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env   # then fill in your API keys
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Run the API server

```bash
cd app && python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

## Code Style

- **Python**: We use [ruff](https://docs.astral.sh/ruff/) for linting. Run `ruff check app/ tests/` before committing.
- **Frontend**: ESLint is configured. Run `npm run lint` in the `frontend/` directory.
- **Commits**: English-only commit messages.

## Testing

```bash
# Backend
pytest -v

# Frontend
cd frontend && npm run lint && npm run build
```

All tests must pass before merging. Tests should not require real API keys — mock external calls.

## Pull Requests

1. Fork the repo and create a feature branch from `main`.
2. Write tests for new functionality.
3. Ensure `ruff check` and `pytest` pass.
4. Open a PR with a clear description of what changed and why.

## Reporting Issues

Open a GitHub issue with:
- Steps to reproduce
- Expected vs. actual behavior
- Python/Node version and OS
