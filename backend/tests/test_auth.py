import uuid
import time
from types import SimpleNamespace

import jwt
import pytest
from fastapi import HTTPException

from app.config import settings
from app import auth


def _fake_candidate():
    return SimpleNamespace(
        id=uuid.uuid4(),
        corporate_id=uuid.uuid4(),
        package_id=uuid.uuid4(),
    )


def test_candidate_token_roundtrip():
    candidate = _fake_candidate()
    token = auth.issue_candidate_token(candidate)
    decoded = jwt.decode(
        token, settings.SECRET_KEY, algorithms=["HS256"], audience=auth.CANDIDATE_AUDIENCE
    )
    assert decoded["sub"] == str(candidate.id)
    assert decoded["corporate_id"] == str(candidate.corporate_id)
    assert decoded["typ"] == "candidate"
    assert decoded["exp"] > time.time()


def _hr_token(corporate_id, secret=None):
    return jwt.encode(
        {
            "sub": str(uuid.uuid4()),
            "aud": "authenticated",
            "exp": int(time.time()) + 3600,
            "app_metadata": {"corporate_id": str(corporate_id)},
        },
        secret or settings.SUPABASE_JWT_SECRET,
        algorithm="HS256",
    )


@pytest.mark.asyncio
async def test_hr_user_valid_token():
    corp = uuid.uuid4()
    ctx = await auth.get_current_hr_user(authorization=f"Bearer {_hr_token(corp)}")
    assert ctx.corporate_id == corp


@pytest.mark.asyncio
async def test_hr_user_missing_token():
    with pytest.raises(HTTPException) as exc:
        await auth.get_current_hr_user(authorization=None)
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_hr_user_bad_signature():
    with pytest.raises(HTTPException) as exc:
        await auth.get_current_hr_user(authorization=f"Bearer {_hr_token(uuid.uuid4(), secret='wrong-secret-value')}")
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_hr_user_no_corporate_context():
    token = jwt.encode(
        {"sub": str(uuid.uuid4()), "aud": "authenticated", "exp": int(time.time()) + 3600, "app_metadata": {}},
        settings.SUPABASE_JWT_SECRET,
        algorithm="HS256",
    )
    with pytest.raises(HTTPException) as exc:
        await auth.get_current_hr_user(authorization=f"Bearer {token}")
    assert exc.value.status_code == 403
