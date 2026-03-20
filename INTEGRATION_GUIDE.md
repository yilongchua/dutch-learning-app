# New App Integration Guide

This guide is the implementation checklist for adding a new app module to the YL unified codebase.

## Principles

- Keep app code isolated in `backend/app/<your_app>/` and matching frontend modules.
- Reuse shared services in `backend/base/` (LLM/TTS/ASR/search) instead of duplicating adapters.
- Use absolute backend imports (`from backend...`).
- Keep data isolated in `data/app/<your_app>/`.

## 1) Backend Integration (FastAPI + SQLModel)

### 1.1 Create app structure

Create:

```text
backend/app/<your_app>/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── config.py
│   └── database.py
├── schema/
│   ├── __init__.py
│   └── models.py
├── service/
│   ├── __init__.py
│   └── logic.py
├── prompts/                 # optional
└── router.py
```

### 1.2 Wire global config

In `backend/config/config.py`:

1. Add `YOURAPP_DATA_DIR = DATA_DIR / "app" / "your_app"`.
2. Add it to the directory auto-create list.
3. Add `YOURAPP_DB_URL` to `Settings`.

### 1.3 Implement app core files

- `core/config.py`: proxy to master settings, including `DATABASE_URL`.
- `core/database.py`: SQLModel engine, `init_db()`, and `get_session()` dependency.
- `schema/models.py`: SQLModel tables for your app domain.
- `service/logic.py`: business logic using `backend/base` helpers where relevant.
- `router.py`: `APIRouter` endpoints.

### 1.4 Register in `backend/main.py`

1. Import the new router and `init_db`.
2. Call `init_<your_app>_db()` in lifespan startup (wrap with `try/except`).
3. Mount with `app.include_router(..., prefix="/api/<your_app>")`.
4. Add app name to the root `apps` metadata response.

### 1.5 Optional background worker pattern

If your app needs pre-generation/sync jobs:

- Put worker logic under `service/`.
- Start/stop worker tasks in FastAPI lifespan (`backend/main.py`) with proper cancellation in `finally`.
- Use lock/guard patterns to prevent duplicate concurrent refill/sync loops.
- Prefer DB-backed work queues over request-time heavy generation.

## 2) Frontend Integration (React Router)

### 2.1 Add API client

Create `frontend/app/services/<your_app>Api.ts`:
- Axios instance with `baseURL` pointing to `/api/<your_app>`.
- Typed request/response interfaces.
- Shared error logging style similar to existing services.

### 2.2 Add routes/components

- Add route module(s) under `frontend/app/routes/`.
- Add reusable UI under `frontend/app/components/<your_app>/` when logic gets large.
- Keep route files focused on page orchestration.

### 2.3 Register navigation

1. Add route entry in `frontend/app/routes.ts`.
2. Add nav item/section in `frontend/app/components/layout/Navbar.tsx`.

### 2.4 Optional shared state

If the app needs cross-route persistence:
- Add a provider under `frontend/app/context/`.
- Mount provider from `frontend/app/root.tsx`.
- Persist only serializable state in local storage; keep blobs/transient objects in memory.

## 3) Verification Checklist

Run these before opening PR:

1. Backend boots cleanly:
   - `cd backend && python main.py`
2. API docs include new app:
   - `http://localhost:8010/docs`
3. Frontend typecheck passes:
   - `cd frontend && npm run typecheck`
4. Frontend navigation renders and route loads from navbar.
5. DB files are created under `data/app/<your_app>/`.

## 4) Common Pitfalls

- Missing `__init__.py` files causing import failures.
- Using relative imports across backend packages.
- Forgetting to add app DB/data dir settings.
- Mounting router but forgetting startup `init_db`.
- Running expensive generation directly in request path when a queue/worker is more appropriate.
