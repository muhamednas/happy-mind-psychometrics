import logging
import pytest
from app.services.email_service import EmailService


@pytest.mark.asyncio
async def test_nudge_simulation_returns_true(monkeypatch, caplog):
    # No provider configured => local simulation path.
    monkeypatch.delenv("SENDGRID_API_KEY", raising=False)
    monkeypatch.delenv("AWS_SES_REGION", raising=False)

    with caplog.at_level(logging.INFO, logger="app.email_service"):
        ok = await EmailService.send_nudge_email(
            email="jane@example.com",
            name="Jane",
            access_code="HM-ABCDEF-1",
            package_title="Engineering Aptitude",
        )

    assert ok is True
    logged = "\n".join(r.getMessage() for r in caplog.records)
    assert "jane@example.com" in logged
    assert "HM-ABCDEF-1" in logged
