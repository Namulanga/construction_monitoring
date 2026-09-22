from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Camera
from app.schemas.common import ListResponse

router = APIRouter()


@router.get("", response_model=ListResponse)
def list_cameras(zone_id: str | None = None, status: str | None = None, db: Session = Depends(get_db)):
    q = db.query(Camera)
    if zone_id:
        q = q.filter(Camera.zone_id == zone_id)
    if status:
        q = q.filter(Camera.status == status)
    return ListResponse(items=[
        {"camera_id": c.camera_id, "zone_id": c.zone_id, "name": c.name, "status": c.status}
        for c in q.all()
    ])