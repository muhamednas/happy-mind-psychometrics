from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.package import PackageCreate, PackageResponse
from app.schemas.candidate import CandidateResponse
from app.services.package_service import PackageService
from app.services.candidate_service import CandidateService

router = APIRouter()

@router.post("/packages/create", response_model=PackageResponse)
async def create_package(package_in: PackageCreate, db: AsyncSession = Depends(get_db)):
    return await PackageService.create_package(db, package_in)

@router.get("/packages", response_model=List[PackageResponse])
async def list_packages(db: AsyncSession = Depends(get_db)):
    return await PackageService.get_packages(db)

@router.get("/packages/{id}", response_model=PackageResponse)
async def get_package(id: UUID, db: AsyncSession = Depends(get_db)):
    package = await PackageService.get_package(db, id)
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")
    return package

@router.get("/candidates", response_model=List[CandidateResponse])
async def list_candidates(package_id: Optional[UUID] = None, db: AsyncSession = Depends(get_db)):
    return await CandidateService.get_candidates(db, package_id=package_id)

@router.get("/candidates/{id}", response_model=CandidateResponse)
async def get_candidate(id: UUID, db: AsyncSession = Depends(get_db)):
    candidate = await CandidateService.get_candidate(db, id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate
