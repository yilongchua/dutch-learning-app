# 🧩 New App Integration Guide

This guide provides step-by-step instructions for AI coding assistants and developers to seamlessly integrate a new modular "App" (e.g., a new learning tool or news feed) into the **YL Unified Application** architecture.

> [!IMPORTANT]
> **Strict Rules:**
> - Do not touch any files outside of the app folder you are working on, unless explicitly modifying the specific routing integrations named below.
> - Always utilize Shared Cores (`backend/base/`) for repetitive LLM/TTS/ComfyUI logic rather than rebuilding custom connections.
> - Utilize the App Proxy model (`core/config.py`) to connect local app configurations to the master database and directory settings.

## 0. Architecture Overview
The application follows a **Modular Monolith** pattern: 
- **Shared Core**: Base utilities found in `backend/base/` (LLM, TTS, Search) and `frontend/app/components/layout/`.
- **Isolated Apps**: Dedicated app subdirectories inside `backend/app/<app_name>/` and a corresponding section in `frontend/`.
- **Data Isolation**: Each app automatically utilizes its own SQLite database stored at `data/app/<app_name>/<app_name>.db`.

---

## Part 1: Backend Integration (FastAPI / SQLModel)

### Step 1.1: Initialize Folder Structure
Create a new directory for your app `backend/app/<your_app>/` with the following subdirectories **and include empty `__init__.py` files in every folder** to ensure Python correctly registers it as an importable package:
```text
backend/app/<your_app>/
├── __init__.py         # CRITICAL: Do not forget this!
├── core/
│   ├── __init__.py     # CRITICAL: Do not forget this!
│   ├── config.py       # Proxy for master settings
│   └── database.py     # SQLModel engine/session setup
├── schema/
│   ├── __init__.py     # CRITICAL: Do not forget this!
│   └── models.py       # SQLModel classes
├── service/
│   ├── __init__.py     # CRITICAL: Do not forget this!
│   └── logic.py        # Business logic linking to Shared Cores
├── prompts/            # Jinja2 templates (.j2 files), if any
└── router.py           # FastAPI APIRouter endpoints
```

### Step 1.2: Update Master Configuration
Open `backend/config/config.py` and systematically add configuration bindings for the new app.
1. **Directory Path**: Define `YOURAPP_DATA_DIR = DATA_DIR / "app" / "yourapp"`.
2. **Directory Creation**: Append `YOURAPP_DATA_DIR` into the existing `for new_dir in [...]` array to ensure auto-creation on server boot.
3. **Database URL**: Inside the `Settings` class, declare your DB variable:
   `YOURAPP_DB_URL: str = Field(default=f"sqlite:///{YOURAPP_DATA_DIR}/yourapp.db", env="YOURAPP_DB_URL")`

### Step 1.3: Set Up App-Specific Logic
1. **Config Proxy (`core/config.py`)**: Map `master_settings.YOURAPP_DB_URL` as a local `DATABASE_URL` proxy logic.
2. **Database Engine (`core/database.py`)**: Initialize the SQLModel engine and provide an `init_db()` and `get_session()` function.
3. **Models & Services**: Create SQLModels in `schema/models.py`, implement your `service/logic.py`, and expose endpoints in `router.py`.

### Step 1.4: Register in `backend/main.py`
To strictly link the new app into the global FastAPI application without breaking others, modify `backend/main.py` in four exact logical blocks:
1. **Imports**: Import `<your_app>_router` from `router.py` and rename `init_db` as `init_<your_app>_db` from `core.database`.
2. **Lifespan Initialization**: Inside the `lifespan()` block, invoke `init_<your_app>_db()` to spin up its SQLite tables successfully upon server startup.
3. **Mounting**: At the bottom of router mounting section, append `app.include_router(<your_app>_router, prefix="/api/<your_app>", tags=["Your App Name"])`.
4. **Root List Updates**: Edit the `async def root()` method and append `"your_app"` to the metadata array for `"apps"`.

---

## Part 2: Frontend Integration (React Router / Vite)

### Step 2.1: Implement API Service Logic
Inside `frontend/app/services/`, create `<your_app>Api.ts`. 
- Utilize Axios initialized to a master base URL falling back correctly onto `.../api/<your_app>` API router prefixes.
- Build heavily annotated TypeScript interfaces mimicking the responses of backend Models, ensuring safe typing.

### Step 2.2: Build Interface Components
1. **App Container Wrapper**: Construct your primary React view page configuring metadata inside `frontend/app/routes/<your_app>.tsx`.
2. **Sub-Component Logic**: Build complex nested logic (forms, lists, real-time polling updates, async loaders) isolated cleanly under `frontend/app/components/<your_app>/`. Avoid dumping all logic into the router file directly!

### Step 2.3: Wire the Global Navigation
1. **React Router Registration**: Open `frontend/app/routes.ts` and append the logical route mapping pointing to your new file:
   `route("your-url", "./routes/<your_app>.tsx"),`
2. **Navbar Registration**: Open `frontend/app/components/layout/Navbar.tsx`.
   - Before editing array objects, **ALWAYS ensure you are importing any new required Icons** from `lucide-react` at the top of the file.
   - Insert a properly styled JSON object node representing your section within the primary `sections` list.

---


## Part 3: Verification & Execution 

1. **Verify Backend Syntax**: CD into `backend/` and run `python main.py`. Ensure there are no unmapped module exceptions (especially from missing `__init__.py` initializers) and verify terminal logs confirm successful SQLite DB creation.
2. **Examine Endpoints**: Access `http://127.0.0.1:8000/docs` evaluating if `<your_app>` API signatures align seamlessly alongside existing apps.
3. **Launch the UI**: Spin up the frontend `npm run dev` and navigate via the `<Navbar>` clicking links manually simulating entire feature connections natively.
