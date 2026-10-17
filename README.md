[English](README.md) | [Русский](README.ru.md)

# Business Management System

[![CI](https://github.com/annaputilovskaya/BusinessManagementSystem/actions/workflows/ci.yml/badge.svg)](https://github.com/annaputilovskaya/BusinessManagementSystem/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/annaputilovskaya/BusinessManagementSystem/graph/badge.svg)](https://codecov.io/gh/annaputilovskaya/BusinessManagementSystem)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-orange.svg)](https://fastapi.tiangolo.com/)

A single-page MVP application (no microservices) for managing a team inside a
company: users with roles, teams, tasks with comments, meetings, evaluations
and a calendar.

**Repo:** [annaputilovskaya/BusinessManagementSystem](https://github.com/annaputilovskaya/BusinessManagementSystem)

## Features

- **Users** (admin / manager / employee roles): self-registration, login/logout,
  profile update, account deletion.
- **Teams**: create a team (admin), add/remove members (admin), assign roles
  inside a team (admin), view team composition (all users).
- **Tasks**: create and assign tasks (manager), change status (executor),
  edit/delete (manager), comments as a simplified chat inside a task
  (manager and executor).
- **Evaluations**: manager scores completed tasks from 1 to 5; a user sees
  personal scores and an average score for a period.
- **Meetings**: schedule a meeting (date, time, participants), overlap check,
  list of the user's meetings, cancel a meeting.
- **Calendar**: tasks and meetings by day and by month.

## Stack

- **Language / framework:** Python 3.11, FastAPI
- **ORM / migrations:** SQLAlchemy 2 (async) + Alembic
- **Database:** PostgreSQL 16
- **Auth / admin:** fastapi-users (JWT, RS256), sqladmin
- **Runtime / tooling:** Docker, docker compose, Poetry
- **Quality:** pytest, pytest-cov, ruff (see [Tests](#tests))

## Architecture

```mermaid
flowchart LR
    Client["Client (REST)"] --> Routers["FastAPI routers"]
    Routers --> Services["services (business logic)"]
    Services --> ORM["SQLAlchemy 2 (async)"]
    ORM --> DB[("PostgreSQL 16")]
    Admin["sqladmin (admin UI)"] --> ORM
    Alembic["Alembic migrations"] --> DB
    Auth["fastapi-users (JWT, RS256)"] --> Routers
```

## Data model

![Database schema](https://github.com/user-attachments/assets/8a665980-8868-4fd5-809a-ec4dd1724f64)

## Business logic

### 1. Users (roles: administrator, manager, regular user)

- Self-registration with email and password
- Authorization / logout
- Profile update
- Account deletion (no recovery)

![Users](https://github.com/user-attachments/assets/6abb2b03-f341-4f81-9e18-df7145582b8b)

### 2. Teams

- Create a team (administrator)
- Add/remove users in a team (administrator)
- View team composition (all users)
- Assign roles to users inside a team (administrator)

![Teams](https://github.com/user-attachments/assets/7d3c7558-4b41-4e9d-be59-bb01f8daa2e9)

### 3. Tasks

- Create tasks (manager)
- Assign an executor (manager)
- Change status (executor)
- Edit/delete (manager)
- Comments — a simplified chat inside a task (manager and executor)

![Tasks](https://github.com/user-attachments/assets/58aca9af-2dd0-4f90-b114-91df285c3a56)

### 4. Work evaluation

- A manager scores completed tasks: 1 to 5 points
- A user sees their scores
- Average score over a period

![Evaluations](https://github.com/user-attachments/assets/bf112e0b-986c-4d4e-815e-704ebafb06d0)

### 5. Meetings

- Schedule a meeting: date, time, participants (user)
- Time check to avoid overlapping events
- List of the user's meetings (meeting participant)
- Ability to cancel a meeting (meeting participant)

![Meetings](https://github.com/user-attachments/assets/a962ab74-f8e0-4bf7-a25c-82dec0e227f5)

### 6. Calendar

- Display tasks and meetings for a day
- Display tasks and meetings for a month

![Calendar](https://github.com/user-attachments/assets/2a36470e-f328-47fa-8044-88193879d452)

## Getting started

### Prerequisites

- Python 3.11+
- [Poetry](https://python-poetry.org/)
- Docker (with docker compose)

### Clone and configure

```bash
git clone https://github.com/annaputilovskaya/BusinessManagementSystem.git
cd BusinessManagementSystem
cp .env.example .env   # Unix; on Windows copy the file manually
```

Fill `.env` with your Postgres credentials, `ALGORITHM=RS256` and token
secrets (see [Configuration](#configuration)).

Generate the JWT certificates for RS256:

```bash
mkdir -p src/auth/certs
openssl genrsa -out src/auth/certs/jwt-private.pem 2048
openssl rsa -in src/auth/certs/jwt-private.pem -pubout -out src/auth/certs/jwt-public.pem
```

Check that Docker is installed:

```bash
docker --version
```

If Docker is not installed, [install it following the official
instructions](https://www.docker.com/).

### Build and run

```bash
docker compose up -d --build
```

The application is available at <http://localhost:8000>, interactive API docs
(Swagger) at <http://localhost:8000/docs>.

## Configuration

All variables are read from `.env` (see `.env.example`).

| Variable | Description | Default |
|---|---|---|
| `POSTGRES_ENGINE` | SQLAlchemy async driver | — |
| `POSTGRES_USER` | Postgres user | — |
| `POSTGRES_PASSWORD` | Postgres password | — |
| `POSTGRES_HOST` | Postgres host | — |
| `POSTGRES_PORT` | Postgres port | — |
| `POSTGRES_DB` | Database name | — |
| `POSTGRES_ECHO` | SQL echo (`0`/`1`) | — |
| `ALGORITHM` | JWT algorithm (RS256) | — |
| `RESET_PASSWORD_TOKEN_SECRET` | Secret for reset-password tokens | — |
| `VERIFICATION_TOKEN_SECRET` | Secret for verification tokens | — |

## API

Interactive documentation (Swagger UI) is available at `/docs`.

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/users/register` | Register a new user |
| `POST` | `/users/login` | Obtain a JWT access token |
| `GET` | `/users/me` | Current user profile |
| `POST` | `/teams/` | Create a team (admin) |
| `PATCH` | `/teams/{team_id}` | Add/remove team members (admin) |
| `GET` | `/teams/` | List teams |
| `POST` | `/tasks/` | Create a task (manager) |
| `GET` | `/tasks/` | List tasks |
| `PATCH` | `/tasks/{task_id}/status` | Change task status (executor) |
| `POST` | `/meetings/` | Schedule a meeting |
| `PATCH` | `/meetings/{meeting_id}` | Cancel a meeting |
| `POST` | `/evaluations/{task_id}` | Score a completed task (manager) |
| `GET` | `/evaluations/average/{executor_id}` | Average score for a user |
| `GET` | `/schedule/day` | Tasks and meetings for a day |
| `GET` | `/schedule/month` | Tasks and meetings for a month |

## Tests

```bash
poetry install
docker compose up -d db        # local Postgres for tests
poetry run pytest --cov=src --cov-fail-under=55
```

Coverage gate: **55%** overall, core business logic (services) **≥ 70%**.
Integration tests run against an isolated test database (`test_<POSTGRES_DB>`)
with migrations applied automatically by the test fixtures.

## Project structure

```
src/
  admin/      # sqladmin views
  alembic/    # migrations
  auth/       # fastapi-users backend, JWT (RS256)
  models/     # SQLAlchemy models (User, Team, Task, Comment, Meeting, Evaluation)
  routers/    # FastAPI routers (users, teams, tasks, meetings, evaluations, schedule)
  schemas/    # Pydantic schemas
  services/   # business logic
tests/        # pytest suite (integration tests on an isolated test DB)
```

## Roadmap / Status

- [x] Users, auth, teams, tasks with comments, meetings, evaluations, calendar
- [x] Core integration tests and coverage gate in CI
- [ ] Real-time comments over WebSocket (JSON protocol, room-scoped broadcast)

## License

MIT — see [LICENSE](LICENSE).
