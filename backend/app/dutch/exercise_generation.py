import asyncio, os, sys, json, random, uuid
# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from sqlmodel import Session, select, distinct
from backend.app.dutch.schema.theme import Theme
from backend.app.dutch.schema.schemas import ExerciseContent
from backend.app.dutch.core.database import engine, init_db
from backend.app.dutch.service.llm_service import LocalLLMService
from backend.base.tts import TTSService
from backend.app.dutch.core.config import settings
class ExerciseGenerator:
    def __init__(self):
        self.llm = LocalLLMService()
        self.tts = TTSService()
        init_db()
        print(f"[*] Initialized Generator.")
        self.current_theme = ""
        
    def _load_themes(self) -> list[str]:
        theme_path = os.path.join(os.path.dirname(__file__), "../../../data/app/dutch/theme.json")
        try:
            with open(theme_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('theme', [])
        except Exception as e:
            print(f"[!] Error loading themes from {theme_path}: {e}")
            return ["Dagelijkse routine"]

    def _add_theme(self, theme_name):
        # Database theme addition is now manual via theme.json
        pass

    def _add_exercise(self, exercise:ExerciseContent):
        with Session(engine) as session:
            session.add(exercise)
            session.commit()
            return True
    
    async def set_theme(self) -> str:
        themes = self._load_themes()
        if not themes:
             return "Dagelijkse routine"
        return random.choice(themes)
    
    async def new_exercise(self, exercise_type: str = 'writing') -> ExerciseContent:
        theme = await self.set_theme()
        return ExerciseContent(theme=theme, exercise_type=exercise_type)

    async def new_writing_exercise(self) -> ExerciseContent:
        exercise = self.new_exercise()
        exercise = await self.llm.generate_exercise(exercise)
        exercise = await self.llm.generate_answer(exercise)
        self._add_exercise(exercise)
        return exercise
    
    async def new_listening_exercise(self) -> ExerciseContent:
        exercise = self.new_exercise('listening')
        exercise = await self.llm.generate_listening(exercise)
        filename = f"{settings.AUDIO_DIR}/tts_{uuid.uuid4().hex}.wav"
        audio_path = self.tts.generate_audio(exercise.audio_text, output_path=filename)
        exercise.audio_url = audio_path
        self._add_exercise(exercise)
        return exercise
