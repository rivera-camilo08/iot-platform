from fastapi import APIRouter

from app.api.v1.endpoints import auth, devices, telemetry, users

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(devices.router, prefix="/devices", tags=["devices"])
api_router.include_router(telemetry.router, prefix="", tags=["telemetry"])
