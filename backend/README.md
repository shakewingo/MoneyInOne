# MoneyInOne Backend API

Backend API service for MoneyInOne iOS financial bookkeeper app, providing asset management, currency conversion, and real-time financial data integration.

## Features

- **Asset Management**: CRUD operations for financial assets (stocks, crypto, bonds, etc.)
- **Multi-Currency Support**: Real-time currency conversion with CNY as primary display currency
- **Real-time Pricing**: Integration with Yahoo Finance, CoinGecko, and exchange rate APIs
- **Portfolio Analytics**: Asset allocation, performance calculations, and summaries
- **Caching Layer**: Redis-based caching for optimal performance
- **Background Jobs**: Celery-based price updates and maintenance tasks

## Technology Stack

- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15+ with SQLAlchemy 2.0
- **Caching**: Redis
- **Background Jobs**: Celery
- **API Documentation**: Automatic OpenAPI/Swagger generation
- **Testing**: Pytest with async support

## Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose (recommended)
- PostgreSQL 15+ (if running locally)
- Redis (if running locally)

### Development Setup with Docker

1. **Clone and navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Copy environment configuration**:
   ```bash
   cp env.example .env
   ```

3. **Start all services**:
   ```bash
   docker-compose up -d
   ```

4. **Run database migrations** (once containers are running):
   ```bash
   docker-compose exec api alembic upgrade head
   ```

5. **Access the API**:
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/api/docs
   - Health Check: http://localhost:8000/health

### Local Development Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up PostgreSQL and Redis** (ensure they're running)

3. **Copy and configure environment**:
   ```bash
   cp env.example .env
   # Edit .env with your local database and Redis URLs
   ```

4. **Run database migrations**:
   ```bash
   alembic upgrade head
   ```

5. **Start the development server**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## API Endpoints

### Health Checks
- `GET /health` - Basic health check
- `GET /api/v1/health/` - Basic health with timestamp
- `GET /api/v1/health/detailed` - Detailed health including database connectivity

### Assets (Coming Soon)
- `GET /api/v1/assets/` - List all assets
- `POST /api/v1/assets/` - Create new asset
- `GET /api/v1/assets/{id}` - Get specific asset
- `PUT /api/v1/assets/{id}` - Update asset
- `DELETE /api/v1/assets/{id}` - Delete asset

## Development Commands

### Code Quality
```bash
# Format code
black app/ tests/

# Lint code
ruff check app/ tests/

# Type checking (if using mypy)
mypy app/
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api.py
```

### Database Operations
```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Background Jobs
```bash
# Start Celery worker (in development)
celery -A app.tasks.celery_app worker --loglevel=info

# Start Celery beat scheduler
celery -A app.tasks.celery_app beat --loglevel=info

# Monitor Celery tasks
celery -A app.tasks.celery_app flower
```

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── assets.py
│   │       │   └── health.py
│   │       └── router.py
│   ├── core/
│   │   ├── config.py
│   │   └── database.py
│   ├── models/          # Database models (coming soon)
│   ├── services/        # Business logic services (coming soon)
│   ├── tasks/           # Celery tasks (coming soon)
│   ├── utils/           # Utility functions (coming soon)
│   └── main.py
├── tests/               # Test files (coming soon)
├── alembic/            # Database migrations (coming soon)
├── requirements.txt
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Environment Variables

See `env.example` for all available configuration options.

Key variables:
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `DEBUG`: Enable debug mode and API docs
- External API keys for financial data providers (optional)

## Contributing

1. Follow the coding standards defined in `pyproject.toml`
2. Write tests for new features
3. Update documentation as needed
4. Ensure all tests pass before submitting changes

## License

Private project - MoneyInOne Team
