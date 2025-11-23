# CrewAI Flow Manager - Backend

FastAPI backend for managing and executing CrewAI flows with real-time updates.

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) - Fast Python package installer
- PostgreSQL 16+

## Quick Start

### Using uv (Recommended)

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env and set OPENAI_API_KEY and DATABASE_URL

# Run development server
uv run uvicorn app.main:app --reload
```

### API Documentation

Once running, visit:
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## Dependencies

Key dependencies (managed via `pyproject.toml`):
- **CrewAI 1.5.0+** - AI agent orchestration framework
- **FastAPI 0.121.3+** - Modern web framework
- **SQLAlchemy 2.0.44+** - ORM for database operations
- **APScheduler 3.10.4+** - Cron-based scheduling
- **Pydantic 2.12.4+** - Data validation
- **Uvicorn 0.38.0+** - ASGI server

## Project Structure

```
backend/
├── app/
│   ├── api/              # API route handlers
│   ├── core/             # Configuration
│   ├── db/               # Database setup
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   └── services/         # Business logic
├── pyproject.toml        # Project dependencies
├── uv.lock              # Locked dependencies
├── .python-version      # Python version (3.11)
└── Dockerfile           # Container definition
```

## Development

### Adding Dependencies

```bash
# Add a new dependency
uv add package-name

# Add a dev dependency
uv add --dev package-name

# Update all dependencies
uv sync --upgrade
```

### Code Quality

```bash
# Format code with ruff
uv run ruff format .

# Lint code
uv run ruff check .

# Auto-fix linting issues
uv run ruff check --fix .
```

### Running Tests

```bash
# Install dev dependencies
uv sync --all-extras

# Run tests (when available)
uv run pytest
```

## Docker

The backend can also run in Docker:

```bash
# Build image
docker build -t crewai-backend .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://..." \
  -e OPENAI_API_KEY="sk-..." \
  crewai-backend
```

## Environment Variables

Required:
- `DATABASE_URL` - PostgreSQL connection string
- `OPENAI_API_KEY` - OpenAI API key for CrewAI

Optional:
- `SECRET_KEY` - Secret key for future authentication
- `DEBUG` - Enable debug mode
- `SCHEDULER_TIMEZONE` - Timezone for scheduler (default: UTC)

See `.env.example` for a complete list.
