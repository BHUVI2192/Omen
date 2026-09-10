from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = 'OMEN API'
    cors_origins: str = 'http://localhost:3000'
    supabase_url: str | None = None
    supabase_service_role_key: str | None = None
    database_url: str | None = None
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

settings = Settings()
