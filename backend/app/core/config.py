from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = 'OMEN API'
    app_env: str = 'development'
    secret_key: str = 'change-me'
    frontend_url: str = 'http://localhost:3000'
    cors_origins: str = 'http://localhost:3000'
    database_url: str = 'postgresql+psycopg://postgres:postgres@localhost:5432/hetu'
    database_pool_size: int = 5
    database_max_overflow: int = 10
    model_dir: str = './ai'
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    market_data_api_url: str | None = None
    market_data_api_key: str | None = None
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

settings = Settings()
