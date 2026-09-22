from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Equipment
from app.schemas.common import ListResponse
from app.schemas.equipment import EquipmentOut

router = APIRouter()


@router.get("", response_model=ListResponse)
def list_equipment(db: Session = Depends(get_db)):
    items = db.query(Equipment).all()
    return ListResponse(items=[EquipmentOut.model_validate(i) for i in items])