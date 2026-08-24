from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db, SessionLocal
from app.models.package import Package
from app.services.tracking_service import TrackingService

router = APIRouter()

async def run_reminders_task(uuid_token: UUID):
    async with SessionLocal() as session:
        try:
            await TrackingService.send_nudge_reminders(session, uuid_token)
        except Exception as e:
            # log background execution error
            import logging
            logging.getLogger("app.tracking_router").error(f"Background nudges failed: {str(e)}")

@router.get("/{uuid_token}")
async def get_tracking(uuid_token: UUID, db: AsyncSession = Depends(get_db)):
    data = await TrackingService.get_tracking_data(db, uuid_token)
    if not data:
        raise HTTPException(status_code=404, detail="Campaign batch not found")
    return data

@router.get("/{uuid_token}/export")
async def export_tracking_csv(uuid_token: UUID, db: AsyncSession = Depends(get_db)):
    csv_data = await TrackingService.generate_candidates_csv(db, uuid_token)
    if csv_data is None:
        raise HTTPException(status_code=404, detail="Campaign batch not found")
        
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=candidates-progress-{uuid_token}.csv"
        }
    )

@router.post("/{uuid_token}/remind")
async def trigger_reminders(
    uuid_token: UUID, 
    background_tasks: BackgroundTasks, 
    db: AsyncSession = Depends(get_db)
):
    # Immediate validation to return 404 if package doesn't exist
    pkg_result = await db.execute(select(Package).where(Package.id == uuid_token))
    package = pkg_result.scalars().first()
    if not package:
        raise HTTPException(status_code=404, detail="Campaign batch not found")
        
    background_tasks.add_task(run_reminders_task, uuid_token)
    return {"message": "Candidate nudge reminder emails queued in background task successfully"}
