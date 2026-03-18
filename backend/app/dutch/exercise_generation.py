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
        with Session(engine) as session:
            themes = session.exec(select(distinct(Theme.name))).all()
        return themes if themes else []

    def _add_theme(self, theme_name):
        with Session(engine) as session:
            session.add(Theme(name=theme_name))
            session.commit()
            return True
    def _add_exercise(self, exercise:ExerciseContent):
        with Session(engine) as session:
            session.add(exercise)
            session.commit()
            return True
    
    async def set_theme(self) -> str:
        if random.random() > 0.8:    
            new_theme = await self.llm.get_new_theme(self._load_themes())
            self._add_theme(new_theme)
            return new_theme
        themes = self._load_themes()
        if not themes:
             new_theme = await self.llm.get_new_theme([])
             self._add_theme(new_theme)
             return new_theme
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
