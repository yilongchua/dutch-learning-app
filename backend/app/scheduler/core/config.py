from backend.config.config import settings as master_settings

class SchedulerSettings:
    DATABASE_URL: str = master_settings.SCHEDULER_DB_URL

settings = SchedulerSettings()
