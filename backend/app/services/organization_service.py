import re
import random
from uuid import UUID
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.organization import Organization
from app.schemas.organization import OrganizationCreate, OrganizationUpdate

class OrganizationService:
    @staticmethod
    async def get_organizations(session: AsyncSession) -> List[Organization]:
        stmt = select(Organization).order_by(Organization.name)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_organization(session: AsyncSession, org_id: UUID) -> Optional[Organization]:
        stmt = select(Organization).where(Organization.id == org_id)
        result = await session.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def get_organization_by_slug(session: AsyncSession, slug: str) -> Optional[Organization]:
        stmt = select(Organization).where(Organization.slug == slug)
        result = await session.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def create_organization(session: AsyncSession, org_in: OrganizationCreate) -> Organization:
        slug = org_in.slug
        if not slug:
            slug = re.sub(r'[^a-z0-9-]', '', org_in.name.lower().replace(' ', '-'))
            if not slug:
                slug = "default-org"
        
        # Check if slug exists, append random suffix if it does
        slug_check = await session.execute(select(Organization).where(Organization.slug == slug))
        if slug_check.scalars().first():
            slug = f"{slug}-{random.randint(1000, 9999)}"

        new_org = Organization(
            name=org_in.name,
            slug=slug,
            logo_url=org_in.logo_url,
            primary_color=org_in.primary_color or "#6366f1",
            quota=org_in.quota or 0,
            used_quota=0
        )
        session.add(new_org)
        await session.commit()
        await session.refresh(new_org)
        return new_org

    @staticmethod
    async def update_organization(session: AsyncSession, org_id: UUID, org_in: OrganizationUpdate) -> Optional[Organization]:
        org = await OrganizationService.get_organization(session, org_id)
        if not org:
            return None
        
        update_data = org_in.model_dump(exclude_unset=True)
        
        # Handle custom slug updates
        if 'slug' in update_data and update_data['slug']:
            slug = update_data['slug']
            slug_check = await session.execute(select(Organization).where(Organization.slug == slug, Organization.id != org_id))
            if slug_check.scalars().first():
                slug = f"{slug}-{random.randint(1000, 9999)}"
            org.slug = slug

        for field, value in update_data.items():
            if field != 'slug':
                setattr(org, field, value)
                
        await session.commit()
        await session.refresh(org)
        return org

    @staticmethod
    async def delete_organization(session: AsyncSession, org_id: UUID) -> bool:
        org = await OrganizationService.get_organization(session, org_id)
        if not org:
            return False
        await session.delete(org)
        await session.commit()
        return True

    @staticmethod
    async def get_white_labeled_config(session: AsyncSession, org_id: UUID) -> Optional[dict]:
        org = await OrganizationService.get_organization(session, org_id)
        if not org:
            return None
        return {
            "name": org.name,
            "slug": org.slug,
            "logo_url": org.logo_url,
            "primary_color": org.primary_color,
            "quota": org.quota,
            "used_quota": org.used_quota,
            "config": {
                "theme": "custom",
                "primary": org.primary_color,
                "logo": org.logo_url
            }
        }
