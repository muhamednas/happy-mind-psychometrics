from uuid import UUID
import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from starlette.concurrency import run_in_threadpool
from app.database import get_db
from app.services.candidate_service import CandidateService
from app.services.package_service import PackageService
from app.services.report_service import ReportService
from app.models.candidate_progress import CandidateProgress
from app.models.assessment import Assessment

router = APIRouter()


@router.get("/{id}/report")
async def generate_candidate_report(id: UUID, db: AsyncSession = Depends(get_db)):
    candidate = await CandidateService.get_candidate(db, id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

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

    output_filename = f"report_{id}.pdf"
    output_path = os.path.join(os.getcwd(), output_filename)

    file_path, is_pdf = await run_in_threadpool(
        ReportService.generate_report,
        candidate_name=candidate.full_name,
        package_title=package.title if package else "",
        results=results_data,
        output_path=output_path,
    )

    return FileResponse(
        path=file_path,
        filename=os.path.basename(file_path),
        media_type="application/pdf" if is_pdf else "text/html",
        headers={"X-Report-Type": "PDF" if is_pdf else "HTML"},
    )
