# Task Manager API

A RESTful task management API built with **FastAPI** and **MongoDB**, featuring JWT authentication, rate limiting, pagination, activity tracking, and structured logging.

---

## Tech Stack

| Component   | Technology                           |
|-------------|--------------------------------------|
| Framework   | FastAPI                              |
| Database    | MongoDB 7 (via Motor async driver)   |
| Auth        | JWT (python-jose) + bcrypt           |
| Validation  | Pydantic v2                          |
| Rate Limit  | slowapi                              |
| Tests       | pytest + httpx (ASGI transport)      |
| Container   | Docker + docker-compose              |

---

## Setup & Run

### Prerequisites

- Python 3.10+ or Docker
- MongoDB 7 (local or via Docker)

### 1. Clone & Configure

```bash
git clone <repo-url> && cd task-manager
cp .env.example .env
# Edit .env if needed (defaults work for local MongoDB)
```

### 2. Run Locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 3. Run with Docker

```bash
docker compose up --build
```

MongoDB and the API start together on `localhost:8000`.

### 4. Run Tests

```bash
pytest tests/ -v
```

Tests use an isolated `task_manager_test` database that is dropped after each run.

---

## Environment Variables

| Variable             | Default                    | Description          |
|----------------------|----------------------------|----------------------|
| `MONGO_URI`          | `mongodb://localhost:27017` | MongoDB connection   |
| `DATABASE_NAME`      | `task_manager`             | Database name        |
| `JWT_SECRET`         | `change-me-in-production`  | Token signing key    |
| `JWT_ALGORITHM`      | `HS256`                    | JWT algorithm        |
| `JWT_EXPIRY_MINUTES` | `60`                       | Token lifetime       |

---

## API Documentation

Interactive docs are available when the server is running:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Auth

#### `POST /auth/register`

Register a new user.

```json
// Request
{ "name": "John", "email": "john@example.com", "password": "secret123" }

// Response 201
{ "id": "...", "name": "John", "email": "john@example.com" }
```

#### `POST /auth/login`

Log in and receive a JWT token.

```json
// Request
{ "email": "john@example.com", "password": "secret123" }

// Response 200
{ "access_token": "eyJ...", "token_type": "bearer" }
```

Rate limit: **30 requests per minute**.

### Projects

All project endpoints (except list) require `Authorization: Bearer <token>`.

#### `POST /projects/` — Create project

```json
// Request
{ "name": "My Project", "description": "A sample", "members": [] }

// Response 201
{ "id": "...", "name": "My Project", "description": "A sample", "owner": "...", "members": [], "created_at": "..." }
```

#### `GET /projects/?page=1&limit=20` — List projects (paginated)

```json
// Response 200
{ "items": [...], "total": 42, "page": 1, "limit": 20, "pages": 3 }
```

#### `GET /projects/{id}` — Get project by ID

```json
// Response 200
{ "id": "...", "name": "My Project", ... }
```

#### `DELETE /projects/{id}` — Delete project (owner only)

```
// Response 204 (no content)
```

Rate limits: **120/min** for reads, **30/min** for writes.

### Tasks

All task endpoints (except list and get-by-ID) require authentication.

#### `POST /tasks/` — Create task

```json
// Request
{ "title": "Implement feature", "description": "...", "status": "todo", "project_id": "...", "assignee": null }

// Response 201
{ "id": "...", "title": "Implement feature", "status": "todo", ... }
```

#### `GET /tasks/?status=todo&assignee=...&due_date=...&project_id=...&page=1&limit=20` — Filtered + paginated

```json
// Response 200
{ "items": [...], "total": 5, "page": 1, "limit": 20, "pages": 1 }
```

All query parameters are optional.

#### `GET /tasks/{id}` — Get task by ID

#### `PUT /tasks/{id}` — Update task

```json
// Request (partial update)
{ "status": "done", "title": "Updated" }

// Response 200
{ "id": "...", "status": "done", ... }
```

#### `DELETE /tasks/{id}`

```
// Response 204
```

### Activity

#### `GET /tasks/{id}/activity?page=1&limit=20` — Task activity log

Requires authentication. Returns a paginated timeline of actions on the task.

```json
// Response 200
{ "items": [
    { "id": "...", "task_id": "...", "user_id": "...", "action": "task.created", "changes": null, "timestamp": "..." },
    { "id": "...", "task_id": "...", "user_id": "...", "action": "task.status_changed", "changes": { "status": { "old": "todo", "new": "done" } }, "timestamp": "..." }
  ], "total": 2, "page": 1, "limit": 20, "pages": 1 }
```

Actions: `task.created`, `task.updated`, `task.status_changed`, `task.deleted`.

### Health

#### `GET /health`

```json
// Response 200
{ "status": "ok" }
```

---

## Postman Collection

Import `Task Manager API.postman_collection.json` into Postman. The collection includes:

- **Collection variables**: `base_url`, `token`, `project_id`, `task_id`
- **Test scripts** that auto-save tokens and IDs after create/login calls
- Pre-filled request bodies and query parameters for all endpoints

---

## Database Design Decisions

### Why MongoDB?

The task manager workload fits MongoDB's strengths:

- **Flexible schema** — Task fields like `assignee`, `due_date`, and `members` are optional and can evolve without migrations
- **Embedded vs. referenced** — Activities are stored in a separate collection (not embedded in tasks) because activity logs grow unboundedly; embedding them would bloat task documents and defeat the 16 MB document limit
- **Document-level atomicity** — Each operation (create/update/delete task) is a single document write; no multi-document transactions needed

### Collections

| Collection    | Key Fields                          | Indexes                                                      |
|---------------|-------------------------------------|--------------------------------------------------------------|
| `users`       | `email`, `hashed_password`          | `email` (unique)                                             |
| `projects`    | `name`, `owner`, `members`          | None (low cardinality, sorted in memory)                     |
| `tasks`       | `title`, `status`, `project_id`, `assignee`, `due_date` | `(project_id, status)`, `(assignee, status)`, `due_date` |
| `activities`  | `task_id`, `user_id`, `action`, `changes`, `timestamp` | `task_id`, `(task_id, timestamp)`                          |

### Index Strategy

- **`email` (unique)** — Ensures no duplicate registrations and provides fast login lookups
- **`(project_id, status)`** — Covers the most common task filter: "show me all tasks in this project with a given status"
- **`(assignee, status)`** — Optimizes "show me my tasks with a given status"
- **`due_date`** — Supports "show me tasks due before a date"
- **`(task_id, timestamp)`** — Enables efficient chronological activity queries per task; the `-1` sort direction matches the "most recent first" default

### Rate Limiting

Three tiers applied via `slowapi`:

| Tier   | Limit     | Endpoints                                           |
|--------|-----------|------------------------------------------------------|
| Auth   | 30/min    | `POST /auth/register`, `POST /auth/login`            |
| Write  | 30/min    | `POST /projects/`, `DELETE /projects/:id`, task mutations |
| Read   | 120/min   | All `GET` endpoints                                  |

Limits are in-memory (reset on server restart).
