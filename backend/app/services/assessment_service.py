from uuid import UUID
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.assessment import Assessment
from app.schemas.assessment import AssessmentCreate, AssessmentUpdate

class AssessmentService:
    @staticmethod
    async def get_assessments(session: AsyncSession) -> List[Assessment]:
        stmt = select(Assessment).order_by(Assessment.title)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_assessment(session: AsyncSession, assessment_id: UUID) -> Optional[Assessment]:
        stmt = select(Assessment).where(Assessment.id == assessment_id)
        result = await session.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def create_assessment(session: AsyncSession, assessment_in: AssessmentCreate) -> Assessment:
        new_assessment = Assessment(
            title=assessment_in.title,
            description=assessment_in.description,
            type=assessment_in.type,
            time_limit_minutes=assessment_in.time_limit_minutes,
            questions=assessment_in.questions
        )
        session.add(new_assessment)
        await session.commit()
        await session.refresh(new_assessment)
        return new_assessment

    @staticmethod
    async def update_assessment(session: AsyncSession, assessment_id: UUID, assessment_in: AssessmentUpdate) -> Optional[Assessment]:
        assessment = await AssessmentService.get_assessment(session, assessment_id)
        if not assessment:
            return None
        
        update_data = assessment_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(assessment, field, value)
            
        await session.commit()
        await session.refresh(assessment)
        return assessment

    @staticmethod
    async def delete_assessment(session: AsyncSession, assessment_id: UUID) -> bool:
        assessment = await AssessmentService.get_assessment(session, assessment_id)
        if not assessment:
            return False
        await session.delete(assessment)
        await session.commit()
        return True
