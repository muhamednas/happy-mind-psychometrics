from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from starlette.concurrency import run_in_threadpool
from app.database import get_db
from app.auth import get_current_hr_user, HRUserContext
from app.services.candidate_service import CandidateService
from app.services.package_service import PackageService
from app.services.report_service import ReportService
from app.services import storage_service
from app.models.candidate_progress import CandidateProgress
from app.models.assessment import Assessment

router = APIRouter()


@router.get("/{id}/report")
async def generate_candidate_report(
    id: UUID,
    hr: HRUserContext = Depends(get_current_hr_user),
    db: AsyncSession = Depends(get_db),
):
    candidate = await CandidateService.get_candidate(db, id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # service_role bypasses RLS, so enforce tenant isolation in code.
    if candidate.corporate_id != hr.corporate_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    package = await PackageService.get_package(db, candidate.package_id)

    progress = (
        await db.execute(select(CandidateProgress).where(CandidateProgress.candidate_id == id))
    ).scalars().all()

    titles = {
        a.id: a.title
        for a in (
            await db.execute(select(Assessment).where(Assessment.package_id == candidate.package_id))
        ).scalars().all()
    }

    results_data = [
        {
            "assessment": titles.get(p.assessment_id, str(p.assessment_id)),
            "score": float(p.score) if p.score is not None else None,
            "status": p.status,
        }
        for p in progress
    ]

    content, is_pdf = await run_in_threadpool(
        ReportService.generate_report_bytes,
        candidate_name=candidate.full_name,
        package_title=package.title if package else "",
        results=results_data,
    )

    # Best-effort archive to Supabase Storage (never blocks the download).
    await run_in_threadpool(
        storage_service.upload_report, candidate.corporate_id, candidate.id, content, is_pdf
    )

    ext = "pdf" if is_pdf else "html"
    return Response(
        content=content,
        media_type="application/pdf" if is_pdf else "text/html",
        headers={
            "Content-Disposition": f'attachment; filename="report-{id}.{ext}"',
            "X-Report-Type": "PDF" if is_pdf else "HTML",
        },
    )
