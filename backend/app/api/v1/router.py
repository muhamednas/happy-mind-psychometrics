from fastapi import APIRouter
from .candidate import router as candidate_router
from .reports import router as reports_router
from .notifications import router as notifications_router
from .chat import router as chat_router

api_router = APIRouter()
# HR admin CRUD (packages/assessments/candidates) is served directly by Supabase
# via supabase-js + RLS (see frontend/src/lib/adminApi.js), so there is no admin
# REST router here. The service keeps the candidate flow, report generation,
# HR-triggered notifications, and the chatbot.
api_router.include_router(candidate_router, prefix="/candidate", tags=["candidate"])
api_router.include_router(reports_router, prefix="/admin/candidates", tags=["reports"])
api_router.include_router(notifications_router, prefix="/admin/candidates", tags=["notifications"])
api_router.include_router(chat_router, prefix="/chat", tags=["chat"])
