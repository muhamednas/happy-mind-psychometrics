from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Happy Mind Psychometric Assessment Platform"
    DEBUG: bool = False

    # Postgres (async driver). Defaults to the local Supabase stack.
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@127.0.0.1:54322/postgres"

    # Secret used to SIGN candidate access tokens (distinct from Supabase's JWT secret).
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    CANDIDATE_TOKEN_TTL_MINUTES: int = 240

    # Supabase settings (server-side).
    SUPABASE_URL: str = "http://127.0.0.1:54321"
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    # Verifies HR access tokens minted by Supabase Auth (HS256).
    SUPABASE_JWT_SECRET: str = "super-secret-jwt-token-with-at-least-32-characters-long"
    SUPABASE_STORAGE_BUCKET: str = "reports"

    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
