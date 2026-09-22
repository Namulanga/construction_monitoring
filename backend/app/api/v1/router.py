from fastapi import APIRouter

from app.api.v1 import (
    equipment,
    zones,
    cameras,
    stages,
    snapshots,
    deviations,
    dashboard,
    reports,
    health,
    schedules,
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(equipment.router, prefix="/equipment", tags=["equipment"])
api_router.include_router(zones.router, prefix="/zones", tags=["zones"])
api_router.include_router(cameras.router, prefix="/cameras", tags=["cameras"])
api_router.include_router(stages.router, prefix="/stages", tags=["stages"])
api_router.include_router(schedules.router, prefix="/schedules", tags=["schedules"])
api_router.include_router(snapshots.router, prefix="/snapshots", tags=["snapshots"])
api_router.include_router(deviations.router, prefix="/deviations", tags=["deviations"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])