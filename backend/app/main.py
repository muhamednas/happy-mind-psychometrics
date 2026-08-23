from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.database import engine
from app.config import settings
import contextlib


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    """Dispose the engine on shutdown.

    The database schema is managed by Supabase migrations (supabase/migrations),
    applied via `supabase db reset` / `supabase migration up` - never by
    metadata.create_all.
    """
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Psychometric Assessment Platform API — Create, administer, and analyze psychological assessments.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "healthy", "service": settings.PROJECT_NAME}
