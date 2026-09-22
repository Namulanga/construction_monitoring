from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Zone
from app.schemas.common import ListResponse

router = APIRouter()


@router.get("", response_model=ListResponse)
def list_zones(db: Session = Depends(get_db)):
    items = db.query(Zone).all()
    return ListResponse(items=[
        {"zone_id": z.zone_id, "name": z.name, "section": z.section, "floor": z.floor}
        for z in items
    ])