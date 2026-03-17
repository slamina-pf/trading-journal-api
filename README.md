# trading-journal-api

REST API for the Trading Journal application, built with Python and Flask.

## Stack

- **Python 3.13**
- **Flask 3.1**
- **SQLAlchemy** + **Flask-Migrate** (ORM + migrations)
- **Flask-JWT-Extended** (authentication)
- **Pydantic v2** (request validation)
- **PyMySQL** (MySQL driver)
- **Poetry** (dependency management)
- **Docker**

> CORS is not configured on the API. All browser traffic is routed through the Next.js reverse proxy, so the API is never hit directly by the browser.

## Structure

```
trading-journal-api/
├── app/
│   ├── __init__.py          # App factory
│   ├── config.py            # Config and TestConfig
│   ├── extensions.py        # SQLAlchemy, Migrate, JWT instances
│   ├── models/
│   │   └── user.py          # User model
│   ├── routes/
│   │   ├── health.py        # GET /health
│   │   └── login.py         # POST /auth/register, /auth/login, PATCH /auth/account
│   └── schemas/
│       └── user.py          # Pydantic schemas for request validation
├── tests/
│   ├── conftest.py          # Fixtures (app, client, db, auth)
│   └── test_auth.py         # Auth endpoint tests
├── run.py
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── .gitignore
```

## Prerequisites

- Docker
- The `trading-journal-database` service must be running and the `trading_journal_net` network must exist

## Setup

```bash
cp .env.example .env
```

## Environment Variables

| Variable        | Default                | Description                        |
|-----------------|------------------------|------------------------------------|
| `FLASK_ENV`     | `development`          | Flask environment                  |
| `FLASK_DEBUG`   | `1`                    | Enable debug mode                  |
| `DB_HOST`       | `trading_journal_db`   | Database container hostname        |
| `DB_PORT`       | `3306`                 | Database port                      |
| `DB_NAME`       | `trading_journal`      | Database name                      |
| `DB_USER`       | `tj_user`              | Database user                      |
| `DB_PASSWORD`   | `tj_pass`              | Database password                  |
| `SECRET_KEY`    | —                      | Flask secret key (change this!)    |
| `JWT_SECRET_KEY`| —                      | JWT signing key (change this!)     |

## Running

```bash
docker-compose up --build -d
```

The API will be available at `http://localhost:5000`.

## Endpoints

### Public

| Method  | Path             | Description                          |
|---------|------------------|--------------------------------------|
| `GET`   | `/health`        | Returns API and DB connection status |
| `POST`  | `/auth/register` | Create a new account                 |
| `POST`  | `/auth/login`    | Login, returns a JWT access token    |

### Protected (requires `Authorization: Bearer <token>`)

| Method  | Path             | Description                          |
|---------|------------------|--------------------------------------|
| `PATCH` | `/auth/account`  | Update username, email, password, bio, avatar |

### Request / Response examples

**POST /auth/register**
```json
{ "username": "john", "email": "john@example.com", "password": "secret123" }
```

**POST /auth/login**
```json
{ "email": "john@example.com", "password": "secret123" }
```
```json
{ "access_token": "<jwt>", "user": { ... } }
```

**PATCH /auth/account** — all fields optional
```json
{ "username": "newname", "email": "new@example.com", "password": "newpass123", "bio": "Trader", "avatar_url": "https://..." }
```

### Validation errors

Invalid requests return `422` with a structured body:
```json
{
  "errors": [
    { "field": "password", "message": "password must be at least 8 characters" }
  ]
}
```

## Database Migrations

```bash
# Initialize migrations (first time only)
docker exec trading_journal_api flask db init

# Create a migration after model changes
docker exec trading_journal_api flask db migrate -m "description"

# Apply migrations
docker exec trading_journal_api flask db upgrade
```

## Tests

Tests run against an in-memory SQLite database — no external services required.

```bash
# Inside the container
docker exec trading_journal_api poetry run pytest -v

# Locally (requires Poetry)
poetry install
poetry run pytest -v
```

## Network

Joins the external Docker network `trading_journal_net` to communicate with the database container at hostname `trading_journal_db`.
