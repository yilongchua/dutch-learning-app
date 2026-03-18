from backend.config.config import settings as master_settings

# This file aliases the master settings to maintain relative imports within the news sub-app
news_settings = master_settings
class SettingsProxy:
    def __getattr__(self, name):
        if name == "DATABASE_URL":
            return master_settings.THENEWS_DB_URL
        return getattr(master_settings, name)

settings = SettingsProxy()