from fastapi import APIRouter
from app.api.v1.endpoints import login, users, stream, upload, history, organization

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(stream.router, prefix="/stream", tags=["stream"])
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
api_router.include_router(history.router, prefix="/history", tags=["history"])
api_router.include_router(organization.router, prefix="/organization", tags=["organization"])
