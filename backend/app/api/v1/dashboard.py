from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Zone, Deviation
from app.schemas.dashboard import DashboardOut, ZoneSummary

router = APIRouter()


@router.get("", response_model=DashboardOut)
def get_dashboard(date: str | None = None, db: Session = Depends(get_db)):
    zones = db.query(Zone).all()
    summaries = []
    for z in zones:
        devs = db.query(Deviation).filter(Deviation.zone_id == z.zone_id).all()
        count = len(devs)
        sri = sum(d.risk for d in devs) / max(len(devs), 1) if devs else 0.0
        if count == 0:
            status = "ok"
        elif sri < 0.5:
            status = "warning"
        else:
            status = "critical"
        summaries.append(ZoneSummary(
            zone_id=z.zone_id, name=z.name, status=status,
            deviations_count=count, sri=round(sri, 2),
        ))
    return DashboardOut(date=date or "", zones=summaries)