from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = 'OMEN API'
    cors_origins: str = 'http://localhost:3000'
    supabase_url: str | None = None
    supabase_service_role_key: str | None = None
    database_url: str | None = None
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    market_data_api_url: str | None = None
    market_data_api_key: str | None = None
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

settings = Settings()
