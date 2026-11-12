from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from supabase import Client, create_client

# Points directly to the .env file in the same folder as config.py
ENV_PATH = Path(__file__).resolve().parent / ".env"


class Settings(BaseSettings):
    supabase_url: str
    supabase_key: str

    model_config = SettingsConfigDict(env_file=ENV_PATH, extra="ignore")


settings = Settings()
supabase: Client = create_client(settings.supabase_url, settings.supabase_key)
