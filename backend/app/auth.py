"""Authentication helpers for the thin FastAPI service.

Two independent token types:
- Candidate tokens: signed by THIS service with SECRET_KEY (candidates are not
  Supabase Auth users; they authenticate with an access code + email).
- HR tokens: access tokens minted by Supabase Auth, verified with
  SUPABASE_JWT_SECRET. The tenant (`corporate_id`) is read from app_metadata.
"""
from uuid import UUID
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.candidate import Candidate
from app.services.candidate_service import CandidateService

CANDIDATE_AUDIENCE = "happy-mind-candidate"


def issue_candidate_token(candidate: Candidate) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(candidate.id),
        "corporate_id": str(candidate.corporate_id),
        "package_id": str(candidate.package_id),
        "typ": "candidate",
        "aud": CANDIDATE_AUDIENCE,
        "iat": now,
        "exp": now + timedelta(minutes=settings.CANDIDATE_TOKEN_TTL_MINUTES),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def _bearer(authorization: str | None) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    return authorization.split(" ", 1)[1].strip()


async def get_current_candidate(
    authorization: str | None = Header(None), db: AsyncSession = Depends(get_db)
) -> Candidate:
    token = _bearer(authorization)
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=["HS256"], audience=CANDIDATE_AUDIENCE
        )
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if payload.get("typ") != "candidate":
        raise HTTPException(status_code=401, detail="Invalid token type")
    try:
        candidate_id = UUID(payload["sub"])
    except (KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token subject")
    candidate = await CandidateService.get_candidate(db, candidate_id)
    if not candidate:
        raise HTTPException(status_code=401, detail="Candidate not found")
    return candidate


class HRUserContext:
    """Resolved identity of an authenticated HR user from a Supabase JWT."""

    def __init__(self, user_id: UUID, corporate_id: UUID, email: str | None = None, role: str | None = None):
        self.user_id = user_id
        self.corporate_id = corporate_id
        self.email = email
        self.role = role


# Cached JWKS client for asymmetric tokens (local `supabase start` uses ES256).
_jwks_client: jwt.PyJWKClient | None = None


def _jwks() -> jwt.PyJWKClient:
    global _jwks_client
    if _jwks_client is None:
        url = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/.well-known/jwks.json"
        _jwks_client = jwt.PyJWKClient(url)
    return _jwks_client


def decode_hr_token(token: str) -> dict:
    """Verify an HR access token.

    Hosted projects and older local stacks mint HS256 tokens with JWT_SECRET.
    Current local `supabase start` mints ES256 tokens; those are verified via JWKS.
    """
    header = jwt.get_unverified_header(token)
    alg = header.get("alg", "HS256")
    decode_kwargs = {"audience": "authenticated"}
    if alg == "HS256":
        return jwt.decode(token, settings.SUPABASE_JWT_SECRET, algorithms=["HS256"], **decode_kwargs)
    key = _jwks().get_signing_key_from_jwt(token).key
    return jwt.decode(token, key, algorithms=[alg], **decode_kwargs)


async def get_current_hr_user(authorization: str | None = Header(None)) -> HRUserContext:
    token = _bearer(authorization)
    try:
        payload = decode_hr_token(token)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    sub = payload.get("sub")
    app_meta = payload.get("app_metadata") or {}
    corporate_id = app_meta.get("corporate_id")
    if not sub or not corporate_id:
        raise HTTPException(status_code=403, detail="No corporate context in token")
    try:
        return HRUserContext(
            user_id=UUID(sub),
            corporate_id=UUID(corporate_id),
            email=payload.get("email"),
            role=app_meta.get("role"),
        )
    except ValueError:
        raise HTTPException(status_code=403, detail="Invalid corporate context")
