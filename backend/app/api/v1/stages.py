from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Stage
from app.schemas.common import ListResponse

router = APIRouter()


@router.get("", response_model=ListResponse)
def list_stages(db: Session = Depends(get_db)):
    items = db.query(Stage).all()
    return ListResponse(items=[
        {"stage_id": s.stage_id, "code": s.code, "name": s.name, "parent_code": s.parent_code}
        for s in items
    ])