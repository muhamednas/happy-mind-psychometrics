from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.candidate import CandidateLogin, CandidateResponse
from app.schemas.response import ResponseSave, ResponseSubmit
from app.services.candidate_service import CandidateService
from app.services.package_service import PackageService

router = APIRouter()

async def get_current_candidate_id(authorization: str = Header(None)) -> UUID:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = authorization.split(" ")[1]
    try:
        return UUID(token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/login", response_model=CandidateResponse)
async def login(login_data: CandidateLogin, db: AsyncSession = Depends(get_db)):
    try:
        candidate = await CandidateService.login(db, login_data)
        candidate.token = str(candidate.id)
        return candidate
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/dashboard")
async def get_dashboard(candidate_id: UUID = Depends(get_current_candidate_id), db: AsyncSession = Depends(get_db)):
    candidate = await CandidateService.get_candidate(db, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    package = await PackageService.get_package(db, candidate.package_id)
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")
    
    # Query progresses
    from app.models.candidate_progress import CandidateProgress
    from sqlalchemy import select
    res = await db.execute(select(CandidateProgress).where(CandidateProgress.candidate_id == candidate_id))
    progresses = res.scalars().all()
    
    progress_map = {p.test_id: p.status for p in progresses}
    
    tests_with_status = []
    for test in (package.tests or []):
        t_id = test.get("id")
        status = progress_map.get(t_id, "NOT_STARTED")
        tests_with_status.append({
            "id": t_id,
            "title": test.get("title", ""),
            "description": test.get("description", ""),
            "status": status.lower()
        })
        
    return {
        "package_title": package.title,
        "candidate_name": candidate.full_name,
        "tests": tests_with_status
    }

@router.get("/test/{test_id}")
async def get_test(test_id: str, candidate_id: UUID = Depends(get_current_candidate_id), db: AsyncSession = Depends(get_db)):
    candidate = await CandidateService.get_candidate(db, candidate_id)
    package = await PackageService.get_package(db, candidate.package_id)
    for t in package.tests:
        if t.get("id") == test_id:
            return t
    raise HTTPException(status_code=404, detail="Test not found")

@router.post("/autosave")
async def autosave(save_data: ResponseSave, candidate_id: UUID = Depends(get_current_candidate_id), db: AsyncSession = Depends(get_db)):
    return await CandidateService.autosave_response(db, candidate_id, save_data)

@router.post("/test/{test_id}/submit")
async def submit_test(test_id: str, candidate_id: UUID = Depends(get_current_candidate_id), db: AsyncSession = Depends(get_db)):
    return await CandidateService.submit_test(db, candidate_id, test_id)
