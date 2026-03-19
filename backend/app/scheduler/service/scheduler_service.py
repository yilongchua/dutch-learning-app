import json
import uuid
import asyncio
from pathlib import Path
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from backend.config.config import settings, SCHEDULER_DATA_DIR

JOBS_FILE = Path(SCHEDULER_DATA_DIR) / "scheduler_jobs.json"

def _load_json() -> list[dict]:
    """Load jobs from the JSON file."""
    if not JOBS_FILE.exists():
        return []
    with open(JOBS_FILE, "r") as f:
        return json.load(f)

def _save_json(jobs: list[dict]):
    """Persist jobs to the JSON file."""
    with open(JOBS_FILE, "w") as f:
        json.dump(jobs, f, indent=2)

def get_all_jobs() -> list[dict]:
    return _load_json()

def add_job(job: dict) -> dict:
    jobs = _load_json()
    job["id"] = str(uuid.uuid4())
    jobs.append(job)
    _save_json(jobs)
    return job

def delete_job(job_id: str) -> bool:
    jobs = _load_json()
    new_jobs = [j for j in jobs if j["id"] != job_id]
    if len(new_jobs) == len(jobs):
        return False
    _save_json(new_jobs)
    return True


# ---------------------------------------------------------------------------
# APScheduler integration
# ---------------------------------------------------------------------------

class SchedulerService:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()

        # Import generators lazily to avoid circular imports at module load time
        from backend.app.dutch.exercise_generation import ExerciseGenerator
        from backend.app.thenews.content_generation import ContentGenerator
        from backend.app.graphics_generation.service.logic import GraphicsGenerationService

        self.dutch_gen = ExerciseGenerator()
        self.news_gen = ContentGenerator()
        self.graphics_gen = GraphicsGenerationService()

    def start(self):
        """Load persisted jobs and start the APScheduler."""
        for job in _load_json():
            self._add_to_apscheduler(job)
        self.scheduler.start()
        print("[*] Scheduler Service started.")

    def _add_to_apscheduler(self, job: dict):
        try:
            time_obj = datetime.strptime(job["schedule_time"], "%I:%M %p")
        except ValueError:
            print(f"[!] Invalid time format for job {job['id']}: {job['schedule_time']}")
            return

        task_map = {
            "dutch": self.run_dutch,
            "thenews": self.run_news,
            "graphics_image": self.run_graphics_image,
            "graphics_video": self.run_graphics_video,
        }
        func = task_map.get(job["task_type"])
        if not func:
            print(f"[!] Unknown task type: {job['task_type']}")
            return

        job_id = job["id"]
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)

        self.scheduler.add_job(
            func,
            "cron",
            hour=time_obj.hour,
            minute=time_obj.minute,
            id=job_id,
            args=[job.get("input_number", 1)],
        )
        print(f"[*] Scheduled '{job['task_type']}' job [{job_id}] at {time_obj.hour:02d}:{time_obj.minute:02d}")

    def add_job_to_scheduler(self, job: dict):
        self._add_to_apscheduler(job)

    def remove_job_from_scheduler(self, job_id: str):
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
            print(f"[*] Removed job [{job_id}] from scheduler.")

    # ------------------------------------------------------------------
    # Task runners
    # ------------------------------------------------------------------

    async def run_dutch(self, input_number: int):
        import random
        print(f"[*] Running 'dutch' scheduled task ({input_number}x)")
        for _ in range(input_number):
            try:
                if random.choice([True, False]):
                    await self.dutch_gen.new_writing_exercise()
                else:
                    await self.dutch_gen.new_listening_exercise()
            except Exception as e:
                print(f"[!] Dutch task error: {e}")

    async def run_news(self, input_number: int):
        print(f"[*] Running 'thenews' scheduled task")
        try:
            await self.news_gen.run_pipeline()
        except Exception as e:
            print(f"[!] News task error: {e}")

    async def run_graphics_image(self, input_number: int):
        print(f"[*] Running 'graphics_image' scheduled task ({input_number}x)")
        for _ in range(input_number):
            try:
                await self.graphics_gen.generate_media("An amazing random landscape", "image")
            except Exception as e:
                print(f"[!] Graphics image task error: {e}")

    async def run_graphics_video(self, input_number: int):
        print(f"[*] Running 'graphics_video' scheduled task ({input_number}x)")
        for _ in range(input_number):
            try:
                await self.graphics_gen.generate_media("An amazing random video scene", "video")
            except Exception as e:
                print(f"[!] Graphics video task error: {e}")


# Singleton
scheduler_service = SchedulerService()
