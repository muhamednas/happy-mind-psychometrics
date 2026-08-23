"""Best-effort upload of generated reports to Supabase Storage.

Uses the service_role key (server-side only). Objects are stored under
`{corporate_id}/{candidate_id}.pdf` so a storage RLS policy can scope HR reads
to their own corporate. Failures are swallowed: the report is always streamed
back to the caller regardless of whether the archive upload succeeds.
"""
import logging
from uuid import UUID

from app.config import settings

logger = logging.getLogger(__name__)


def upload_report(corporate_id: UUID, candidate_id: UUID, content: bytes, is_pdf: bool) -> str | None:
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
        return None

    ext = "pdf" if is_pdf else "html"
    path = f"{corporate_id}/{candidate_id}.{ext}"
    content_type = "application/pdf" if is_pdf else "text/html"

    try:
        from supabase import create_client

        client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
        client.storage.from_(settings.SUPABASE_STORAGE_BUCKET).upload(
            path,
            content,
            {"content-type": content_type, "upsert": "true"},
        )
        return path
    except Exception as exc:  # noqa: BLE001 - archiving is best-effort
        logger.warning("Report storage upload failed for %s: %s", path, exc)
        return None
