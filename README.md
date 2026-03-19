# YL Unified Application

A modular application designed to integrate multiple micro-apps (e.g., **TheNews** and **Dutch B1**) into a single, cohesive ecosystem. The project follows a "Package-as-App" philosophy, allowing for rapid scaling and distinct data isolation.

## 📁 Directory Structure

```text
Dutch/
├── backend/            # Fast API Unified Server
│   ├── app/            # Micro-apps (dutch, thenews)
│   ├── base/           # Core shared services (LLM, TTS, ASR)
│   ├── config/         # Unified settings and DB paths
│   └── main.py         # Entry point (Unified Router)
├── frontend/           # React Router Unified UI
│   ├── app/
│   │   ├── components/ # Centralized layout and app components
│   │   └── services/   # Unified API clients
├── data/               # Persistent storage (Git-ignored)
│   └── app/            # App-specific SQLite databases
└── README.md
```

---

## 🚀 Quick Start

### 1. Prerequisites

- **Python 3.9+** (Conda environment `fastapi_env` recommended)
- **Node.js** (for Frontend)
- **Local LLM Server** (LM Studio / Ollama running on `http://localhost:1234`)
- **ComfyUI** (for image generation server on port `8188`)

### 2. Backend Setup

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

_Server runs at: `http://localhost:8000`_

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

_UI runs at: `http://localhost:5173`_

---

---

## 🏗 Modular App Architecture

The system is designed to be easily extensible. For a step-by-step walkthrough on how to add a new micro-app (like **TheNews** or **Dutch B1**), please refer to the:

## 👉 **[New App Integration Guide](./INTEGRATION_GUIDE.md)**

## 🛑 Troubleshooting

If you encounter "Address already in use" errors, you can kill the existing processes using:

- **Backend (8000)**: `lsof -ti:8010 | xargs kill -9`
- **Frontend (5173)**: `lsof -ti:5173 | xargs kill -9`

### Key Architectural Guidelines:

- **Data Isolation**: Each app is responsible for its own directory in `data/app/<app_name>/`.
- **Package-as-App**: All app-specific logic, schemas, and prompts live in `backend/app/<app_name>/`.
- **Unified Routing**: Apps are mounted via routers in `backend/main.py` under the `/api/` prefix.
- **Shared Core**: Use the utilities in `backend/base/` for LLM, TTS, ASR, and Search.

### Shared Services (`base/`)

- **llm_base.py**: Unified interface for local LLMs with Template support.
- **tts.py**: Cross-platform Speech-to-Text with XTTS v2 and macOS fallback.
- **websearch_service.py**: Integrated SearXNG and content extraction.

---

## 📜 Project Rules & Standards

- **Imports**: Always use absolute package imports starting with `backend.` (e.g., `from backend.app.dutch...`).
- **Data Unification**: Whenever possible, unify exercise patterns into the standard `ExerciseContent` schema.
- **State Management**: Prefer stateless APIs where state is handled by the unified databases.
