from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.candidate import Candidate
from app.models.package import Package
from app.models.candidate_progress import CandidateProgress
from app.models.candidate_response import CandidateResponse
from app.schemas.candidate import CandidateLogin
from app.schemas.response import ResponseSave

class CandidateService:
    @staticmethod
    async def login(session: AsyncSession, login_data: CandidateLogin) -> Candidate:
        pkg_result = await session.execute(select(Package).where(Package.access_code == login_data.access_code, Package.is_active == True))
        package = pkg_result.scalars().first()
        if not package:
            raise ValueError("Invalid access code")
        
        cand_result = await session.execute(
            select(Candidate).where(Candidate.email == login_data.email, Candidate.access_code == login_data.access_code)
        )
        candidate = cand_result.scalars().first()
        
        if not candidate:
            candidate = Candidate(
                package_id=package.id,
                full_name=login_data.email.split('@')[0],
                email=login_data.email,
                access_code=login_data.access_code
            )
            session.add(candidate)
        
        candidate.logged_in_at = datetime.now(timezone.utc).replace(tzinfo=None)
        await session.commit()
        await session.refresh(candidate)
        return candidate
    
    @staticmethod
    async def get_candidate(session: AsyncSession, candidate_id: UUID) -> Candidate:
        result = await session.execute(select(Candidate).where(Candidate.id == candidate_id))
        return result.scalars().first()
        
    @staticmethod
    async def get_candidates(session: AsyncSession, package_id: UUID = None):
        stmt = select(Candidate)
        if package_id:
            stmt = stmt.where(Candidate.package_id == package_id)
        result = await session.execute(stmt)
        candidates = result.scalars().all()
        
        tracker_list = []
        for cand in candidates:
            # Fetch package
            pkg_result = await session.execute(select(Package).where(Package.id == cand.package_id))
            pkg = pkg_result.scalars().first()
            package_title = pkg.title if pkg else "Unknown Package"
            total_tests = len(pkg.tests) if (pkg and pkg.tests) else 0
            
            # Fetch candidate progresses
            from app.models.candidate_progress import CandidateProgress
            prog_result = await session.execute(
                select(CandidateProgress).where(CandidateProgress.candidate_id == cand.id)
            )
            progresses = prog_result.scalars().all()
            completed_tests = sum(1 for p in progresses if p.status == "COMPLETED")
            in_progress_tests = sum(1 for p in progresses if p.status == "IN_PROGRESS")
            
            status = "not_started"
            if total_tests > 0 and completed_tests == total_tests:
                status = "completed"
            elif completed_tests > 0 or in_progress_tests > 0 or cand.logged_in_at:
                status = "in_progress"
                
            progress_str = f"{completed_tests}/{total_tests}"
            
            scores = [p.score for p in progresses if p.score is not None]
            avg_score = f"{round(sum(scores)/len(scores), 1)}%" if scores else "-"
            
            # Populate extra fields
            cand.package_title = package_title
            cand.status = status
            cand.progress = progress_str
            cand.score = avg_score
            tracker_list.append(cand)
            
        return tracker_list
    
    @staticmethod
    async def autosave_response(session: AsyncSession, candidate_id: UUID, save_data: ResponseSave):
        prog_result = await session.execute(
            select(CandidateProgress).where(CandidateProgress.candidate_id == candidate_id, CandidateProgress.test_id == save_data.test_id)
        )
        progress = prog_result.scalars().first()
        if not progress:
            progress = CandidateProgress(
                candidate_id=candidate_id,
                test_id=save_data.test_id,
                status="IN_PROGRESS",
                started_at=datetime.now(timezone.utc).replace(tzinfo=None)
            )
            session.add(progress)
        elif progress.status == "NOT_STARTED":
            progress.status = "IN_PROGRESS"
            progress.started_at = datetime.now(timezone.utc).replace(tzinfo=None)
            
        resp_result = await session.execute(
            select(CandidateResponse).where(
                CandidateResponse.candidate_id == candidate_id, 
                CandidateResponse.test_id == save_data.test_id,
                CandidateResponse.question_id == save_data.question_id
            )
        )
        response = resp_result.scalars().first()
        if response:
            response.response = save_data.response
        else:
            response = CandidateResponse(
                candidate_id=candidate_id,
                test_id=save_data.test_id,
                question_id=save_data.question_id,
                response=save_data.response
            )
            session.add(response)
            
        await session.commit()
        return response

    @staticmethod
    async def submit_test(session: AsyncSession, candidate_id: UUID, test_id: str):
        prog_result = await session.execute(
            select(CandidateProgress).where(CandidateProgress.candidate_id == candidate_id, CandidateProgress.test_id == test_id)
        )
        progress = prog_result.scalars().first()
        if not progress:
            progress = CandidateProgress(
                candidate_id=candidate_id,
                test_id=test_id
            )
            session.add(progress)
            
        progress.status = "COMPLETED"
        progress.completed_at = datetime.now(timezone.utc).replace(tzinfo=None)
        
        import random
        progress.score = round(random.uniform(50.0, 100.0), 2)
        
        await session.commit()
        return progress
