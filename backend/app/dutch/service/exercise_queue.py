import asyncio
from datetime import datetime, timezone

from sqlmodel import Session, select, func

from backend.app.dutch.core.database import engine
from backend.app.dutch.exercise_generation import ExerciseGenerator
from backend.app.dutch.schema.schemas import ExerciseContent

EXERCISE_TYPES = ("writing", "listening", "speaking")
MIN_PENDING_PER_TYPE = 5
REFILL_INTERVAL_SECONDS = 30


class DutchExerciseQueueService:
    def __init__(self):
        self.generator = ExerciseGenerator()
        self._refill_lock = asyncio.Lock()
        self._loop_task: asyncio.Task | None = None

    async def get_next_exercise(self, category: str, theme: str) -> ExerciseContent:
        now = datetime.now(timezone.utc)
        with Session(engine) as session:
            preferred_stmt = (
                select(ExerciseContent)
                .where(ExerciseContent.exercise_type == category)
                .where(ExerciseContent.status == "pending")
                .where(ExerciseContent.theme == theme)
                .order_by(ExerciseContent.created_at.asc())
                .limit(1)
            )
            exercise = session.exec(preferred_stmt).first()

            if exercise is None:
                fallback_stmt = (
                    select(ExerciseContent)
                    .where(ExerciseContent.exercise_type == category)
                    .where(ExerciseContent.status == "pending")
                    .order_by(ExerciseContent.created_at.asc())
                    .limit(1)
                )
                exercise = session.exec(fallback_stmt).first()

            if exercise is not None:
                exercise.status = "served"
                exercise.updated_at = now
                session.add(exercise)
                session.commit()
                session.refresh(exercise)
                return exercise

        # Emergency fallback on miss: generate one now and serve it immediately.
        generated = await self.generator.generate_by_type(category)
        with Session(engine) as session:
            persisted = session.get(ExerciseContent, generated.id)
            if persisted is None:
                persisted = generated
                session.add(persisted)
                session.commit()
                session.refresh(persisted)

            persisted.status = "served"
            persisted.updated_at = now
            session.add(persisted)
            session.commit()
            session.refresh(persisted)
            return persisted

    async def refill_if_needed(self):
        if self._refill_lock.locked():
            return

        async with self._refill_lock:
            for exercise_type in EXERCISE_TYPES:
                pending_count = self._count_pending(exercise_type)
                missing = max(0, MIN_PENDING_PER_TYPE - pending_count)
                for _ in range(missing):
                    try:
                        await self.generator.generate_by_type(exercise_type)
                    except Exception as exc:
                        print(f"[!] Refill failed for {exercise_type}: {exc}")
                        break

    def _count_pending(self, exercise_type: str) -> int:
        with Session(engine) as session:
            stmt = (
                select(func.count())
                .select_from(ExerciseContent)
                .where(ExerciseContent.exercise_type == exercise_type)
                .where(ExerciseContent.status == "pending")
            )
            return int(session.exec(stmt).one() or 0)

    def start_background_refill(self):
        if self._loop_task and not self._loop_task.done():
            return
        self._loop_task = asyncio.create_task(self._run_refill_loop())

    async def stop_background_refill(self):
        if self._loop_task:
            self._loop_task.cancel()
            try:
                await self._loop_task
            except asyncio.CancelledError:
                pass
            self._loop_task = None

    async def _run_refill_loop(self):
        while True:
            await self.refill_if_needed()
            await asyncio.sleep(REFILL_INTERVAL_SECONDS)


exercise_queue_service = DutchExerciseQueueService()
