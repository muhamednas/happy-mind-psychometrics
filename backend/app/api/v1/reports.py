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

router = APIRouter()

@router.get("/{id}/report")
async def generate_candidate_report(id: UUID, db: AsyncSession = Depends(get_db)):
    candidate = await CandidateService.get_candidate(db, id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    package = await PackageService.get_package(db, candidate.package_id)
    
    result = await db.execute(select(CandidateProgress).where(CandidateProgress.candidate_id == id))
    progress = result.scalars().all()
    
    results_data = [{"test_id": p.test_id, "score": p.score, "status": p.status} for p in progress]
    
    output_filename = f"report_{id}.pdf"
    output_path = os.path.join(os.getcwd(), output_filename)
    
    file_path, is_pdf = await run_in_threadpool(
        ReportService.generate_report,
        candidate_name=candidate.full_name,
        package_title=package.title,
        results=results_data,
        output_path=output_path
    )
    
    response_filename = os.path.basename(file_path)
    media_type = "application/pdf" if is_pdf else "text/html"
    
    return FileResponse(
        path=file_path,
        filename=response_filename,
        media_type=media_type,
        headers={"X-Report-Type": "PDF" if is_pdf else "HTML"}
    )
