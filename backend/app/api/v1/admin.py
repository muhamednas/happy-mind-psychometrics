from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.package import PackageCreate, PackageResponse
from app.schemas.candidate import CandidateResponse
from app.schemas.organization import OrganizationCreate, OrganizationResponse, OrganizationUpdate
from app.schemas.assessment import AssessmentCreate, AssessmentResponse, AssessmentUpdate
from app.services.package_service import PackageService
from app.services.candidate_service import CandidateService
from app.services.organization_service import OrganizationService
from app.services.assessment_service import AssessmentService

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
    return await CandidateService.get_candidates(db, package_id)

@router.get("/candidates/{id}", response_model=CandidateResponse)
async def get_candidate(id: UUID, db: AsyncSession = Depends(get_db)):
    candidate = await CandidateService.get_candidate(db, id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate

# Corporate Client Routes
@router.get("/corporates", response_model=List[OrganizationResponse])
async def list_corporates(db: AsyncSession = Depends(get_db)):
    return await OrganizationService.get_organizations(db)

@router.post("/corporates", response_model=OrganizationResponse)
async def create_corporate(org_in: OrganizationCreate, db: AsyncSession = Depends(get_db)):
    return await OrganizationService.create_organization(db, org_in)

@router.get("/corporates/{id}", response_model=OrganizationResponse)
async def get_corporate(id: UUID, db: AsyncSession = Depends(get_db)):
    org = await OrganizationService.get_organization(db, id)
    if not org:
        raise HTTPException(status_code=404, detail="Corporate client not found")
    return org

@router.put("/corporates/{id}", response_model=OrganizationResponse)
async def update_corporate(id: UUID, org_in: OrganizationUpdate, db: AsyncSession = Depends(get_db)):
    org = await OrganizationService.update_organization(db, id, org_in)
    if not org:
        raise HTTPException(status_code=404, detail="Corporate client not found")
    return org

@router.delete("/corporates/{id}")
async def delete_corporate(id: UUID, db: AsyncSession = Depends(get_db)):
    success = await OrganizationService.delete_organization(db, id)
    if not success:
        raise HTTPException(status_code=404, detail="Corporate client not found")
    return {"message": "Corporate client deleted successfully"}

@router.get("/corporates/{id}/config")
async def get_corporate_config(id: UUID, db: AsyncSession = Depends(get_db)):
    config = await OrganizationService.get_white_labeled_config(db, id)
    if not config:
        raise HTTPException(status_code=404, detail="Corporate client configuration not found")
    return config

# Assessment Library Routes
@router.get("/assessments", response_model=List[AssessmentResponse])
async def list_assessments(db: AsyncSession = Depends(get_db)):
    return await AssessmentService.get_assessments(db)

@router.post("/assessments", response_model=AssessmentResponse)
async def create_assessment(assessment_in: AssessmentCreate, db: AsyncSession = Depends(get_db)):
    return await AssessmentService.create_assessment(db, assessment_in)

@router.get("/assessments/{id}", response_model=AssessmentResponse)
async def get_assessment(id: UUID, db: AsyncSession = Depends(get_db)):
    assessment = await AssessmentService.get_assessment(db, id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return assessment

@router.put("/assessments/{id}", response_model=AssessmentResponse)
async def update_assessment(id: UUID, assessment_in: AssessmentUpdate, db: AsyncSession = Depends(get_db)):
    assessment = await AssessmentService.update_assessment(db, id, assessment_in)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return assessment

@router.delete("/assessments/{id}")
async def delete_assessment(id: UUID, db: AsyncSession = Depends(get_db)):
    success = await AssessmentService.delete_assessment(db, id)
    if not success:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return {"message": "Assessment deleted successfully"}
