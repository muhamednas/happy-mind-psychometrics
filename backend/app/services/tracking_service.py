import io
import csv
from uuid import UUID
from typing import Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.package import Package
from app.models.organization import Organization
from app.services.candidate_service import CandidateService
from app.services.email_service import EmailService

class TrackingService:
    @staticmethod
    def mask_name(name: str) -> str:
        if not name:
            return ""
        parts = name.split()
        masked = []
        for p in parts:
            if len(p) > 2:
                masked.append(p[0] + "*" * (len(p) - 2) + p[-1])
            elif len(p) > 1:
                masked.append(p[0] + "*")
            else:
                masked.append(p)
        return " ".join(masked)

    @staticmethod
    def mask_email(email: str) -> str:
        if not email:
            return ""
        try:
            local, domain = email.split('@', 1)
            if len(local) > 2:
                masked_local = local[0] + "*" * (len(local) - 2) + local[-1]
            elif len(local) > 0:
                masked_local = local[0] + "*" * (len(local) - 1)
            else:
                masked_local = ""
            return f"{masked_local}@{domain}"
        except Exception:
            return email

    @staticmethod
    async def get_tracking_data(session: AsyncSession, uuid_token: UUID) -> Optional[Dict[str, Any]]:
        # Fetch package
        pkg_result = await session.execute(select(Package).where(Package.id == uuid_token))
        package = pkg_result.scalars().first()
        if not package:
            return None

        # Fetch org
        org_result = await session.execute(select(Organization).where(Organization.id == package.organization_id))
        org = org_result.scalars().first()
        org_name = org.name if org else "Unknown Organization"

        # Fetch candidates with computed status details
        candidates = await CandidateService.get_candidates(session, package_id=uuid_token)

        # Compute stats
        total_invited = len(candidates)
        completed = sum(1 for c in candidates if c.status == "completed")
        in_progress = sum(1 for c in candidates if c.status == "in_progress")
        not_started = sum(1 for c in candidates if c.status == "not_started")

        # Mask candidates lists (no access codes returned)
        masked_candidates = []
        for c in candidates:
            masked_candidates.append({
                "id": c.id,
                "name": TrackingService.mask_name(c.full_name),
                "email": TrackingService.mask_email(c.email),
                "status": c.status,
                "progress": c.progress,
                "score": c.score if c.status == "completed" else "-",
                "logged_in_at": c.logged_in_at.isoformat() if c.logged_in_at else None,
                "report_url": f"/api/v1/admin/candidates/{c.id}/report" if c.status == "completed" else None
            })

        return {
            "package_id": package.id,
            "package_title": package.title,
            "organization_name": org_name,
            "stats": {
                "total_invited": total_invited,
                "completed": completed,
                "in_progress": in_progress,
                "not_started": not_started
            },
            "candidates": masked_candidates
        }

    @staticmethod
    async def send_nudge_reminders(session: AsyncSession, uuid_token: UUID) -> Dict[str, Any]:
        # Fetch package
        pkg_result = await session.execute(select(Package).where(Package.id == uuid_token))
        package = pkg_result.scalars().first()
        if not package:
            raise ValueError("Campaign batch not found")

        # Fetch candidates with computed status details
        candidates = await CandidateService.get_candidates(session, package_id=uuid_token)

        # Filter candidates needing reminder (not completed)
        nudged_emails = []
        for c in candidates:
            if c.status in ["not_started", "in_progress"]:
                # Use raw candidate details to send actual reminder email
                success = await EmailService.send_nudge_email(
                    email=c.email,
                    name=c.full_name,
                    access_code=c.access_code,
                    package_title=package.title
                )
                if success:
                    nudged_emails.append(TrackingService.mask_email(c.email))

        return {
            "message": "Nudge reminders processed successfully",
            "reminders_sent_count": len(nudged_emails),
            "nudged_recipients": nudged_emails
        }

    @staticmethod
    async def generate_candidates_csv(session: AsyncSession, uuid_token: UUID) -> Optional[str]:
        # Fetch package
        pkg_result = await session.execute(select(Package).where(Package.id == uuid_token))
        package = pkg_result.scalars().first()
        if not package:
            return None

        # Fetch candidates with computed status details
        candidates = await CandidateService.get_candidates(session, package_id=uuid_token)

        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(["Candidate Name", "Candidate Email", "Status", "Progress Completed", "Average Score", "Logged In At"])
        
        # Write data rows
        for c in candidates:
            writer.writerow([
                TrackingService.mask_name(c.full_name),
                TrackingService.mask_email(c.email),
                c.status,
                c.progress,
                c.score if c.status == "completed" else "-",
                c.logged_in_at.isoformat() if c.logged_in_at else "Never"
            ])
            
        return output.getvalue()
