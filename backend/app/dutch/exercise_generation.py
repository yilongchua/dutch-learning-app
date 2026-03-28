import asyncio, os, sys, json, random, uuid
# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from sqlmodel import Session, select, distinct
from backend.app.dutch.schema.schemas import ExerciseContent, SpeakingWritingExercise, ListeningExercise
from backend.app.dutch.core.database import engine, init_db
from backend.app.dutch.service.llm_service import LocalLLMService
from backend.base.tts import TTSService
from backend.app.dutch.core.config import settings, master_settings
from backend.config.config import DATA_DIR
class ExerciseGenerator:
    def __init__(self):
        self.llm = LocalLLMService()
        self.tts = TTSService()
        init_db()
        print(f"[*] Initialized Generator.")
        self.current_theme = ""
        self.basic_theme = "Dagelijkse routine"
        
    def _load_themes(self) -> list[str]:
        theme_path = DATA_DIR / "app"/"dutch"/"theme.json"
        try:
            with open(str(theme_path), 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('theme', [])
        except Exception as e:
            print(f"[!] Error loading themes from {theme_path}: {e}")
            return [self.basic_theme]

    def _add_exercise(self, exercise:ExerciseContent):
        with Session(engine) as session:
            session.add(exercise)
            session.commit()
            session.refresh(exercise)
            return exercise
    
    async def set_theme(self) -> str:
        themes = self._load_themes()
        if not themes:
             return self.basic_theme
        return random.choice(themes)

    async def new_exercise(self, exercise_type: str) -> ExerciseContent:
        theme = await self.set_theme()
        return ExerciseContent(theme=theme, exercise_type=exercise_type, status="pending")

    async def new_speak_write_exercise(self, theme) ->SpeakingWritingExercise:
        """Writing and Speaking Exercise"""
        exercise = SpeakingWritingExercise()
        
        result = await self.llm.generate_exercise(theme)
        exercise.question = result.question
        exercise.keywords = result.keywords

        result = await self.llm.generate_answer(question=result.question, keywords=result.keywords)
        exercise.correct_answer = result.structured_dutch
        
        result = await self.llm.translate_answer(result.structured_dutch)
        exercise.correct_answer_translation = result.translated_english
        return exercise

    async def new_listening_exercise(self, theme:str) -> ListeningExercise:
        exercise = ListeningExercise()
        result = await self.llm.generate_listening(theme)
        exercise.audio_text = result.text
        exercise.audio_translation = result.english_translation
        exercise.questions = result.exercises

        filename = f"{master_settings.AUDIO_DIR}/tts_{uuid.uuid4().hex}.wav"
        audio_path = self.tts.generate_audio(exercise.audio_text, output_path=filename)
        exercise.audio_url = audio_path
        return exercise
    async def generate_by_type(self, exercise_type: str) -> ExerciseContent:
        exercise = await self.new_exercise(exercise_type)
        if exercise_type in ["writing", "speaking"]:
            gen_exercise =  await self.new_speak_write_exercise(exercise.theme)
        elif exercise_type == "listening":
            gen_exercise =  await self.new_listening_exercise(exercise.theme)
        else:
            raise ValueError(f"Unsupported exercise type: {exercise_type}")
        exercise.exercise =  gen_exercise
        return self._add_exercise(exercise)