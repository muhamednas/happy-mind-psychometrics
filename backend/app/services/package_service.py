import re
import random
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.package import Package
from app.models.assessment import Assessment
from app.models.candidate import Candidate
from app.models.corporate import Corporate
from app.schemas.package import PackageCreate
from app.services.code_generator import generate_access_code


class PackageService:
    @staticmethod
    async def _get_or_create_corporate(session: AsyncSession, name: str) -> Corporate:
        """Transitional helper. Once admin CRUD moves to supabase-js (Phase 4),
        the corporate comes from the authenticated HR user instead of a name."""
        name = (name or "").strip() or "Default Org"
        result = await session.execute(select(Corporate).where(Corporate.name == name))
        corp = result.scalars().first()
        if corp:
            return corp

        slug = re.sub(r"[^a-z0-9-]", "", name.lower().replace(" ", "-")) or "default-org"
        slug_check = await session.execute(select(Corporate).where(Corporate.slug == slug))
        if slug_check.scalars().first():
            slug = f"{slug}-{random.randint(1000, 9999)}"
        corp = Corporate(name=name, slug=slug)
        session.add(corp)
        await session.flush()
        return corp

    @staticmethod
    async def create_package(session: AsyncSession, package_in: PackageCreate) -> Package:
        corp = await PackageService._get_or_create_corporate(session, package_in.organization_name)

        code = await generate_access_code(session)
        new_package = Package(
            corporate_id=corp.id,
            title=package_in.title,
            description=package_in.description,
            access_code=code,
        )
        session.add(new_package)
        await session.flush()

        for position, test in enumerate(package_in.tests):
            session.add(
                Assessment(
                    corporate_id=corp.id,
                    package_id=new_package.id,
                    title=test.title,
                    description=test.description,
                    time_limit_minutes=test.time_limit_minutes,
                    position=position,
                    questions=test.questions,
                )
            )

        await session.commit()
        await session.refresh(new_package)
        return new_package

    @staticmethod
    async def get_packages(session: AsyncSession, corporate_id: UUID | None = None):
        stmt = (
            select(Package, func.count(Candidate.id).label("candidate_count"))
            .outerjoin(Candidate, Candidate.package_id == Package.id)
            .group_by(Package.id)
        )
        if corporate_id:
            stmt = stmt.where(Package.corporate_id == corporate_id)
        result = await session.execute(stmt)
        packages = []
        for pkg, count in result.all():
            pkg.candidate_count = count
            packages.append(pkg)
        return packages

    @staticmethod
    async def get_package(session: AsyncSession, package_id: UUID):
        stmt = (
            select(Package, func.count(Candidate.id).label("candidate_count"))
            .outerjoin(Candidate, Candidate.package_id == Package.id)
            .where(Package.id == package_id)
            .group_by(Package.id)
        )
        result = await session.execute(stmt)
        row = result.first()
        if row:
            pkg, count = row
            pkg.candidate_count = count
            return pkg
        return None

    @staticmethod
    async def get_assessments(session: AsyncSession, package_id: UUID):
        result = await session.execute(
            select(Assessment).where(Assessment.package_id == package_id).order_by(Assessment.position)
        )
        return result.scalars().all()
