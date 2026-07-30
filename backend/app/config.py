from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Happy Mind Psychometric Assessment Platform"
    DEBUG: bool = False
    SECRET_KEY: str = "supersecretkey"
    DATABASE_URL: str = "sqlite+aiosqlite:///./happymind.db"
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


settings = Settings()
