# YL Unified Application

YL is a unified modular platform that hosts multiple apps (currently Dutch B1, TheNews, Graphics Generation, and Scheduler) in one backend and one frontend.

The architecture is a modular monolith:
- App code is isolated by folder (`backend/app/<app_name>`, matching frontend routes/services).
- Data is isolated per app under `data/app/<app_name>/`.
- Shared infrastructure (LLM, TTS, ASR, search, config) lives in `backend/base/` and `backend/config/`.

## Directory Layout

```text
thesystem/
├── backend/
│   ├── app/                  # app modules: dutch, thenews, graphics_generation, scheduler
│   ├── base/                 # shared service wrappers (LLM/TTS/ASR/search)
│   ├── config/               # global settings + per-app data paths
│   └── main.py               # FastAPI entrypoint + unified router mounting
├── frontend/
│   └── app/
│       ├── routes/           # route-level pages
│       ├── services/         # API clients by app
│       ├── components/       # reusable UI
│       └── context/          # shared client state (e.g., Dutch session state)
├── data/                     # runtime DB/media data (git-ignored)
├── INTEGRATION_GUIDE.md
└── README.md
```

## Quick Start

### 1) Prerequisites
- Python 3.9+
- Node.js 18+
- Local LLM endpoint (default: `http://localhost:1234/v1`)
- ComfyUI (only needed for graphics generation features)

### 2) Backend

```bash
cd backend
# 1. Prepare environment variables (Copy .env.example from root)
cp ../.env.example ../.env

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download NLP models
python -m spacy download nl_core_news_sm

# 4. Start the server
python main.py
```

Backend default URL: `http://localhost:8010`
Swagger docs: `http://localhost:8010/docs`

### 3) Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend default URL: `http://localhost:5173`

## Environment Notes

Primary runtime settings are in `backend/config/config.py` and can be overridden by `.env`.

Important variables:
- `BACKEND_PORT` (default `8010`)
- `FRONTEND_PORT` (default `5173`)
- `LOCAL_LLM_URL`
- `MODEL`
- `DUTCH_DB_URL`, `THENEWS_DB_URL`, `GRAPHICS_GENERATION_DB_URL`
- `IMAGE_DIR`, `AUDIO_DIR`

## Current App Behaviors

- Dutch app now serves exercises DB-first from a pre-generated queue and refills in the background.
- Dutch frontend state (writing/speaking/listening session progress) persists across page navigation and refresh using shared context + local storage.
- TheNews and Graphics Generation remain mounted through the same unified backend.

## Integration Guide

For adding a new app module, follow:

[`INTEGRATION_GUIDE.md`](./INTEGRATION_GUIDE.md)

## Troubleshooting

Port already in use:
- Backend (`8010`): `lsof -ti:8010 | xargs kill -9`
- Frontend (`5173`): `lsof -ti:5173 | xargs kill -9`

Model/dependency issues:
- Reinstall Python deps: `pip install -r backend/requirements.txt`
- Re-download spaCy Dutch model: `python -m spacy download nl_core_news_sm`

## Development Rules

- Use absolute backend imports starting with `backend.`.
- Keep app-specific logic within its own app folder.
- Reuse shared services in `backend/base/` rather than duplicating integrations.
- Prefer DB-backed state for durable backend workflows and keep frontend state thin/predictable.
