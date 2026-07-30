from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.package import Package
from app.models.candidate import Candidate
from app.schemas.package import PackageCreate
from app.services.code_generator import generate_access_code

class PackageService:
    @staticmethod
    async def create_package(session: AsyncSession, package_in: PackageCreate) -> Package:
        from app.models.organization import Organization
        import re
        import random

        org_name = package_in.organization_name.strip()
        slug = re.sub(r'[^a-z0-9-]', '', org_name.lower().replace(' ', '-'))
        if not slug:
            slug = "default-org"

        org_result = await session.execute(select(Organization).where(Organization.name == org_name))
        org = org_result.scalars().first()
        if not org:
            # Check if slug exists
            slug_check = await session.execute(select(Organization).where(Organization.slug == slug))
            if slug_check.scalars().first():
                slug = f"{slug}-{random.randint(1000, 9999)}"
            org = Organization(name=org_name, slug=slug)
            session.add(org)
            await session.commit()
            await session.refresh(org)

        code = await generate_access_code(session)
        new_package = Package(
            organization_id=org.id,
            title=package_in.title,
            description=package_in.description,
            tests=package_in.tests,
            access_code=code
        )
        session.add(new_package)
        await session.commit()
        await session.refresh(new_package)
        return new_package

    @staticmethod
    async def get_packages(session: AsyncSession):
        stmt = select(Package, func.count(Candidate.id).label("candidate_count")).outerjoin(Candidate).group_by(Package.id)
        result = await session.execute(stmt)
        packages = []
        for pkg, count in result.all():
            pkg.candidate_count = count
            packages.append(pkg)
        return packages

    @staticmethod
    async def get_package(session: AsyncSession, package_id: UUID):
        stmt = select(Package, func.count(Candidate.id).label("candidate_count")).outerjoin(Candidate).where(Package.id == package_id).group_by(Package.id)
        result = await session.execute(stmt)
        row = result.first()
        if row:
            pkg, count = row
            pkg.candidate_count = count
            return pkg
        return None
