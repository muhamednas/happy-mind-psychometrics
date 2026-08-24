from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.auth import get_current_hr_user, HRUserContext
from app.services.candidate_service import CandidateService
from app.services.package_service import PackageService
from app.services.email_service import EmailService

router = APIRouter()


@router.post("/{id}/nudge")
async def nudge_candidate(
    id: UUID,
    hr: HRUserContext = Depends(get_current_hr_user),
    db: AsyncSession = Depends(get_db),
):
    """Send a reminder email to a candidate. HR-only, tenant-scoped."""
    candidate = await CandidateService.get_candidate(db, id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    # service_role bypasses RLS, so enforce tenant isolation in code.
    if candidate.corporate_id != hr.corporate_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    package = await PackageService.get_package(db, candidate.package_id)
    sent = await EmailService.send_nudge_email(
        email=candidate.email,
        name=candidate.full_name,
        access_code=candidate.access_code,
        package_title=package.title if package else "your assessment",
    )
    if not sent:
        raise HTTPException(status_code=502, detail="Failed to send email")
    return {"sent": True, "candidate_id": str(candidate.id)}
