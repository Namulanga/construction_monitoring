from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Deviation
from app.schemas.common import ListResponse
from app.schemas.snapshot import DeviationOut

router = APIRouter()


@router.get("", response_model=ListResponse)
def list_deviations(
    zone_id: str | None = None,
    stage_id: str | None = None,
    type: str | None = None,
    from_: str | None = None,
    to: str | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(Deviation)
    if zone_id:
        q = q.filter(Deviation.zone_id == zone_id)
    if stage_id:
        q = q.filter(Deviation.stage_id == stage_id)
    if type:
        q = q.filter(Deviation.type == type)
    items = q.order_by(Deviation.created_at.desc()).limit(200).all()
    return ListResponse(items=[DeviationOut.model_validate(d) for d in items])


@router.get("/{deviation_id}", response_model=DeviationOut)
def get_deviation(deviation_id: str, db: Session = Depends(get_db)):
    d = db.get(Deviation, deviation_id)
    if not d:
        raise HTTPException(404, "Not found")
    return DeviationOut.model_validate(d)