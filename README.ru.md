[English](README.md) | [Русский](README.ru.md)

# Система управления бизнесом

[![CI](https://github.com/annaputilovskaya/BusinessManagementSystem/actions/workflows/ci.yml/badge.svg)](https://github.com/annaputilovskaya/BusinessManagementSystem/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/annaputilovskaya/9e13be2e22bb6c48cd869d453e37e8fa/raw/coverage.json)](https://github.com/annaputilovskaya/BusinessManagementSystem/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-orange.svg)](https://fastapi.tiangolo.com/)

API для управления командой внутри компании: пользователи с ролями, команды,
задачи с комментариями в реальном времени (WebSocket), встречи, оценка работы и
календарь.

## Возможности

### 1. Пользователи (роли: администратор, менеджер, обычный пользователь)

- Самостоятельная регистрация с email и паролем
- Авторизация / выход
- Обновление профиля
- Удаление аккаунта (без восстановления)

![Пользователи](https://github.com/user-attachments/assets/6abb2b03-f341-4f81-9e18-df7145582b8b)

### 2. Команды

- Создание команды (администратор)
- Добавление/удаление пользователей в команде (администратор)
- Просмотр состава команды (все пользователи)
- Назначение пользователям ролей в команде (администратор)

![Команды](https://github.com/user-attachments/assets/7d3c7558-4b41-4e9d-be59-bb01f8daa2e9)

### 3. Задачи

- Создание задач руководителем (менеджер)
- Назначение исполнителя (менеджер)
- Изменение статуса (исполнитель)
- Изменение / удаление (менеджер)
- Комментарии в реальном времени (WebSocket) внутри задачи (менеджер и исполнитель)

![Задачи](https://github.com/user-attachments/assets/2ea7fae9-ba38-4faf-ae62-3c5c5f7830bf)

### 4. Оценка работы

- Руководитель оценивает выполненные задачи: баллы от 1 до 5
- Пользователь видит свои оценки
- Вывод средней оценки за период

![Оценки](https://github.com/user-attachments/assets/79f86bbe-9c87-4a7b-b276-9e8ed90c9f50)

### 5. Встречи

- Назначение встречи: дата, время, участники (пользователь)
- Проверка времени, чтобы не накладывались события
- Список встреч пользователя (участник встречи)
- Возможность отменить встречу (участник встречи)

![Встречи](https://github.com/user-attachments/assets/a962ab74-f8e0-4bf7-a25c-82dec0e227f5)

### 6. Календарь

- Отображение задач и встреч за день
- Отображение задач и встреч за месяц

![Календарь](https://github.com/user-attachments/assets/2a36470e-f328-47fa-8044-88193879d452)

## Стек

- **Язык / фреймворк:** Python 3.11, FastAPI
- **ORM / миграции:** SQLAlchemy 2 (async) + Alembic
- **Хранение данных:** PostgreSQL 16
- **Auth / admin:** fastapi-users (JWT, RS256), sqladmin
- **Запуск / инструменты:** Docker, docker compose, Poetry
- **Качество:** pytest, pytest-cov, ruff (см. [Тесты](#тесты))

## Архитектура

```mermaid
flowchart LR
    Client["Клиент (REST)"] --> Routers["FastAPI routers"]
    Routers --> Services["services (бизнес-логика)"]
    Services --> ORM["SQLAlchemy 2 (async)"]
    ORM --> DB[("PostgreSQL 16")]
    Admin["sqladmin (админ-UI)"] --> ORM
    Alembic["Alembic (миграции)"] --> DB
    Auth["fastapi-users (JWT, RS256)"] --> Routers
```

## Модель данных

![Схема базы данных](https://github.com/user-attachments/assets/8a665980-8868-4fd5-809a-ec4dd1724f64)

## Комментарии в реальном времени

Комментарии к задачам передаются по WebSocket: `ws /tasks/{task_id}/comments/?token=<jwt>`.

- При подключении сервер отправляет историю комментариев как JSON-массив:
  `[{"type": "comment", "user_id": "...", "text": "...", "created_at": "..."}]`
- Клиенты отправляют `{"text": "..."}`; сервер сохраняет комментарий и рассылает
  `{"type": "comment", ...}` всем участникам, подключённым к комнате этой задачи.
- Некорректные кадры получают `{"type": "error", ...}` без разрыва соединения.
- Отсутствующий/недействительный токен или задача вне вашей команды закрывают
  соединение с кодом 1008.

```mermaid
sequenceDiagram
    participant C as Client
    participant S as FastAPI
    participant DB as PostgreSQL
    C->>S: WS connect ?token=JWT
    S->>DB: verify task access
    S-->>C: history (JSON array)
    C->>S: {"text": "..."}
    S->>DB: add_comment
    S-->>C: broadcast {"type": "comment", ...} (task room)
```

## Запуск

### Требования

- Python 3.11+
- [Poetry](https://python-poetry.org/)
- Docker (с docker compose)

### Клонирование и настройка

```bash
git clone https://github.com/annaputilovskaya/BusinessManagementSystem.git
cd BusinessManagementSystem
cp .env.example .env   # для Unix-подобных систем; в Windows скопируйте файл вручную
```

Заполните `.env` данными Postgres, `ALGORITHM=RS256` и секретами токенов
(см. [Конфигурация](#конфигурация)).

Сгенерируйте JWT-сертификаты для RS256:

```bash
mkdir -p src/auth/certs
openssl genrsa -out src/auth/certs/jwt-private.pem 2048
openssl rsa -in src/auth/certs/jwt-private.pem -pubout -out src/auth/certs/jwt-public.pem
```

Убедитесь, что установлен Docker:

```bash
docker --version
```

Если Docker не установлен,
[осуществите его установку по инструкции с официального сайта](https://www.docker.com/).

### Сборка и запуск

```bash
docker compose up -d --build
```

Приложение доступно по адресу <http://localhost:8000>, интерактивная
документация API (Swagger) — на <http://localhost:8000/docs>.

## Конфигурация

Все переменные читаются из `.env` (см. `.env.example`).

| Переменная | Описание | По умолчанию |
|---|---|---|
| `POSTGRES_ENGINE` | Async-драйвер SQLAlchemy | — |
| `POSTGRES_USER` | Пользователь Postgres | — |
| `POSTGRES_PASSWORD` | Пароль Postgres | — |
| `POSTGRES_HOST` | Хост Postgres | — |
| `POSTGRES_PORT` | Порт Postgres | — |
| `POSTGRES_DB` | Имя базы данных | — |
| `POSTGRES_ECHO` | SQL-echo (`0`/`1`) | — |
| `ALGORITHM` | Алгоритм JWT (RS256) | — |
| `RESET_PASSWORD_TOKEN_SECRET` | Секрет токенов сброса пароля | — |
| `VERIFICATION_TOKEN_SECRET` | Секрет токенов верификации | — |
| `ADMIN_SECRET_KEY` | Секрет для подписи сессии админки | — |

## Тесты

```bash
poetry install
docker compose up -d db        # локальный Postgres для тестов
poetry run pytest --cov=src --cov-fail-under=55
```

Порог покрытия: **55%** общий, ядро бизнес-логики (services) **≥ 70%**.
Интеграционные тесты выполняются на изолированной тестовой БД
(`test_<POSTGRES_DB>`), миграции применяются автоматически фикстурами.

## Структура проекта

```
src/
  admin/      # представления sqladmin
  alembic/    # миграции
  auth/       # бэкенд fastapi-users, JWT (RS256)
  models/     # модели SQLAlchemy (User, Team, Task, Comment, Meeting, Evaluation)
  routers/    # роутеры FastAPI (users, teams, tasks, meetings, evaluations, schedule)
  schemas/    # Pydantic-схемы
  services/   # бизнес-логика
tests/        # набор pytest (интеграционные тесты на изолированной БД)
```

## Лицензия

MIT — см. [LICENSE](LICENSE).
