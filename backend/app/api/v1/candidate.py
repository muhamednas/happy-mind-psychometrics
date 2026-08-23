from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.candidate import Candidate
from app.schemas.candidate import CandidateLogin, CandidateResponse
from app.schemas.response import ResponseSave
from app.services.candidate_service import CandidateService
from app.auth import issue_candidate_token, get_current_candidate

router = APIRouter()


@router.post("/login", response_model=CandidateResponse)
async def login(login_data: CandidateLogin, db: AsyncSession = Depends(get_db)):
    try:
        candidate = await CandidateService.login(db, login_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    candidate.token = issue_candidate_token(candidate)
    return candidate


@router.get("/dashboard")
async def get_dashboard(
    candidate: Candidate = Depends(get_current_candidate), db: AsyncSession = Depends(get_db)
):
    return await CandidateService.get_dashboard(db, candidate)


@router.get("/test/{assessment_id}")
async def get_test(
    assessment_id: UUID,
    candidate: Candidate = Depends(get_current_candidate),
    db: AsyncSession = Depends(get_db),
):
    assessment = await CandidateService.get_assessment_for_candidate(db, candidate, assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Test not found")
    return {
        "id": str(assessment.id),
        "title": assessment.title,
        "description": assessment.description,
        "time_limit_minutes": assessment.time_limit_minutes,
        "questions": assessment.questions,
    }


@router.post("/autosave")
async def autosave(
    save_data: ResponseSave,
    candidate: Candidate = Depends(get_current_candidate),
    db: AsyncSession = Depends(get_db),
):
    resp = await CandidateService.autosave_response(db, candidate, save_data)
    return {"id": str(resp.id), "saved_at": resp.saved_at}


@router.post("/test/{assessment_id}/submit")
async def submit_test(
    assessment_id: UUID,
    candidate: Candidate = Depends(get_current_candidate),
    db: AsyncSession = Depends(get_db),
):
    try:
        progress = await CandidateService.submit_test(db, candidate, assessment_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {
        "assessment_id": str(progress.assessment_id),
        "status": progress.status,
        "score": float(progress.score) if progress.score is not None else None,
        "completed_at": progress.completed_at,
    }
