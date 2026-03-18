# Graphics Generation App - Implementation Plan

## Goal
Develop a new modular app called `graphics_generation` integrated into the YL Unified Application. The app provides a chat-like interface for users to generate images and videos using ComfyUI. Features include an endless scrolling history, a prompt improvement tool powered by an LLM, and the ability to delete past generations.

## Proposed Changes

### Backend System Integration
Modify central configuration to register the new app securely mapping all initial lifecycle injections.

#### [MODIFY] [backend/config/config.py](file:///Users/ryan_chua/Library/CloudStorage/GoogleDrive-neatherlands.sweeden@gmail.com/My%20Drive/8.%20YL%20DS%20Projects/Dutch/backend/config/config.py)
- Add `GRAPHICS_GENERATION_DATA_DIR = DATA_DIR / "app" / "graphics_generation"`.
- Iterate and inject the directory mapping into the startup arrays avoiding non-existent data folder bugs.
- Map `GRAPHICS_GENERATION_DB_URL` pointing safely onto the SQLite generation payload natively in `Settings`.

#### [MODIFY] [backend/main.py](file:///Users/ryan_chua/Library/CloudStorage/GoogleDrive-neatherlands.sweeden@gmail.com/My%20Drive/8.%20YL%20DS%20Projects/Dutch/backend/main.py)
- Import `graphics_generation_router`. 
- **CRITICAL COMPONENT ADDED:** Explicitly import `init_db` assigned as `init_graphics_db`.
- **CRITICAL COMPONENT ADDED:** Ensure `init_graphics_db()` is placed sequentially inside the FastAPI `@asynccontextmanager def lifespan(app)` function correctly spinning up tables locally on booting.
- Bind app logic with `.include_router()`. Add metadata to `root()` listing.

---

### Backend App Module (`backend/app/graphics_generation/`)
Create the isolated backend components natively for the new app avoiding systemic overlaps.

#### [NEW] `__init__.py` Modules (DETECTED MISSING IMPLEMENTATION)
- Generate absolutely necessary blank `__init__.py` files sequentially in the root `graphics_generation/` and recursively into `/core`, `/schema`, `/service`, `/prompts`. Failing to include these throws major unresolved package routing import bugs into FastAPI.

#### [NEW] `core/config.py` & `core/database.py`
- Import and alias the generic master database engine setups dynamically pulling proxy parameters mapping perfectly onto specific DB_URL references cleanly.

#### [NEW] `schema/models.py`
- Construct strict SQLModels holding memory contexts encapsulating:
  - Timestamps (`created_at`) 
  - `original_prompt` versus `improved_prompt` comparisons.
  - Streaming ID trackers. `media_url` logic acts initially heavily tracking temporary prompt completion UUIDs instead of pure links asynchronously formatting execution outcomes.

#### [NEW] `service/logic.py`
- Bridge classes strictly enforcing encapsulation pointing directly to `LLMBase` for LLM integrations and `ComfyUIService` extracting API queues seamlessly masking Comfy API.

#### [NEW] `router.py`
- `/enhance-prompt`: Resolving Jinja generation logic externally.
- `/generate`: Inject initial uncompleted generation payloads onto SQLite saving UUID tracking markers.
- `/history` & `/history/{item_id}`: Standard HTTP fetches/purging maps natively handling endless streams.
- **CRITICAL COMPONENT ADDED:** Add a recursive `/status/{prompt_id}` GET endpoint bypassing internal backend blocking states parsing JSON checks returning live ComfyUI progression dictionary updates.

---

### Frontend App Module (`frontend/`)
Create UI mapping cleanly interpreting reactive data flows dynamically.

#### [MODIFY] [frontend/app/routes.ts](file:///Users/ryan_chua/Library/CloudStorage/GoogleDrive-neatherlands.sweeden@gmail.com/My%20Drive/8.%20YL%20DS%20Projects/Dutch/frontend/app/routes.ts)
- Bind generic endpoint mapping logically inserting UI wrappers.

#### [MODIFY] [frontend/app/components/layout/Navbar.tsx](file:///Users/ryan_chua/Library/CloudStorage/GoogleDrive-neatherlands.sweeden@gmail.com/My%20Drive/8.%20YL%20DS%20Projects/Dutch/frontend/app/components/layout/Navbar.tsx)
- **CRITICAL COMPONENT ADDED:** Manually import required graphics elements targeting `<ImageIcon>` equivalents from `lucide-react` to prevent undefined compilation errors.
- Assemble UI Navigation elements styling explicitly linking `/graphics-generation`.

#### [NEW] `frontend/app/services/graphicsGenerationApi.ts`
- Develop robust Axios connection services integrating heavily typed endpoints linking exclusively back over onto HTTP ports processing `/api/graphics_generation/` scopes securely.
- **CRITICAL COMPONENT ADDED:** Add `.checkStatus()` async integration binding.

#### [NEW] `frontend/app/components/graphics_generation/ChatInterface.tsx` (and related components)
Build the required UI components:
- **Message Feed**: Endless scrolling container displaying history.
- **Message Item**: Displays text, generated image/video, and a dark grey `Delete` button beside each message.
- **Input Area** (Bottom Fixed):
  - **`+` Button**: Located on the left side. Calls `improve-prompt` and fills the text area without auto-sending.
  - **Text Input**: For the 1-3 sentence user description.
  - **Image/Video Slider**: Toggle to select `media_type`.
  - **Send Button**: Triggers the actual `generate` API call.

- **Asynchronous Pollable Display Render Engine:** Break up individual memory instances dynamically linking internal React `useEffect()` hooks executing `setInterval` logic querying `.checkStatus` outputs continuously updating parsing URL logic transforming generated UUID nodes into natively accessible `${COMFY_URL}/view?filename=x` DOM assets without blocking primary UI interfaces.
- Design fully persistent endless messaging containers matching UI requests. Implement specific floating enhancement UI tools gracefully swapping variables conditionally rendering loader interfaces securely.

## Verification Plan

### Automated / Startup Verification
1. **Backend Initialization**: Run `cd backend && python main.py`. Ensure terminal logs show the creation of `data/app/graphics_generation/` and the `.db` file without import errors.
2. **Swagger Docs**: Navigate to `/docs` to ensure the 4 new `graphics_generation` endpoints are listed.

### Manual Verification
1. **UI & Navigation**: Start the frontend (`npm run dev`). Verify the app is visible in the Navbar and navigating to it shows the Chat Interface.
2. **Prompt Improvement**: Type a short sentence, click the "+" button. Verify the text area updates with a longer prompt gracefully, without triggering image generation.
3. **Media Generation**: Toggle the slider to "Image", hit "Send". Verify a loader appears and eventually the generated image is appended to the chat. Repeat for "Video".
4. **Endless Scrolling**: Reload the page to confirm that historical records are fetched and displayed in chronological order.
5. **Deletion**: Click the dark grey delete button on a specific message. Confirm it disappears from the UI and is removed upon page reload.

