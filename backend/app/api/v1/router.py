from fastapi import APIRouter
from .admin import router as admin_router
from .candidate import router as candidate_router
from .reports import router as reports_router
from .chat import router as chat_router

api_router = APIRouter()
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])
api_router.include_router(candidate_router, prefix="/candidate", tags=["candidate"])
api_router.include_router(reports_router, prefix="/admin/candidates", tags=["reports"])
api_router.include_router(chat_router, prefix="/chat", tags=["chat"])
