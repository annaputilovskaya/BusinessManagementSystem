[English](README.md) | [Русский](README.ru.md)

# Система управления бизнесом

[![CI](https://github.com/annaputilovskaya/BusinessManagementSystem/actions/workflows/ci.yml/badge.svg)](https://github.com/annaputilovskaya/BusinessManagementSystem/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/annaputilovskaya/BusinessManagementSystem/graph/badge.svg)](https://codecov.io/gh/annaputilovskaya/BusinessManagementSystem)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-orange.svg)](https://fastapi.tiangolo.com/)

**Задача:** разработать одностраничное MVP-приложение без микросервисов для
управления командой внутри компании: пользователи с ролями, команды, задачи с
комментариями, встречи, оценки и календарь.

**Репозиторий:** [annaputilovskaya/BusinessManagementSystem](https://github.com/annaputilovskaya/BusinessManagementSystem)

## Возможности

- **Пользователи** (роли администратор, менеджер и обычный пользователь):
  самостоятельная регистрация с email и паролем, авторизация/выход, обновление
  профиля, удаление аккаунта.
- **Команды**: создание команды (администратор), добавление/удаление
  пользователей, назначение ролей внутри команды (администратор), просмотр
  состава команды (все пользователи).
- **Задачи**: создание задач руководителем (менеджер), назначение исполнителя
  (менеджер), изменение статуса (исполнитель), изменение/удаление (менеджер),
  комментарии — упрощённый чат внутри задачи (менеджер и исполнитель).
- **Оценка работы**: руководитель оценивает выполненные задачи баллами от 1 до 5;
  пользователь видит свои оценки и вывод средней оценки за период.
- **Встречи**: назначение встречи (дата, время, участники), проверка пересечений,
  список встреч пользователя, отмена встречи.
- **Календарь**: отображение задач и встреч за день и за месяц.

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

## Бизнес-логика

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
- Комментарии — упрощённый чат внутри задачи (менеджер и исполнитель)

![Задачи](https://github.com/user-attachments/assets/58aca9af-2dd0-4f90-b114-91df285c3a56)

### 4. Оценка работы

- Руководитель оценивает выполненные задачи: баллы от 1 до 5
- Пользователь видит свои оценки
- Вывод средней оценки за период

![Оценки](https://github.com/user-attachments/assets/bf112e0b-986c-4d4e-815e-704ebafb06d0)

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

## API

Интерактивная документация (Swagger UI) доступна на `/docs`.

| Метод | Эндпоинт | Описание |
|---|---|---|
| `POST` | `/users/register` | Регистрация пользователя |
| `POST` | `/users/login` | Получение JWT-токена |
| `GET` | `/users/me` | Профиль текущего пользователя |
| `POST` | `/teams/` | Создание команды (администратор) |
| `PATCH` | `/teams/{team_id}` | Добавление/удаление участников (администратор) |
| `GET` | `/teams/` | Список команд |
| `POST` | `/tasks/` | Создание задачи (менеджер) |
| `GET` | `/tasks/` | Список задач |
| `PATCH` | `/tasks/{task_id}/status` | Изменение статуса задачи (исполнитель) |
| `POST` | `/meetings/` | Назначение встречи |
| `PATCH` | `/meetings/{meeting_id}` | Отмена встречи |
| `POST` | `/evaluations/{task_id}` | Оценка выполненной задачи (менеджер) |
| `GET` | `/evaluations/average/{executor_id}` | Средняя оценка пользователя |
| `GET` | `/schedule/day` | Задачи и встречи за день |
| `GET` | `/schedule/month` | Задачи и встречи за месяц |

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

## Roadmap / Статус

- [x] Пользователи, авторизация, команды, задачи с комментариями, встречи, оценки, календарь
- [x] Интеграционные тесты ядра и порог покрытия в CI
- [ ] Комментарии в реальном времени по WebSocket (JSON-протокол, broadcast по комнатам)

## Лицензия

MIT — см. [LICENSE](LICENSE).
