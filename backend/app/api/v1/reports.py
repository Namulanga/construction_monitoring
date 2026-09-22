import csv
import io
from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Deviation

router = APIRouter()


@router.post("")
def create_report(from_: str | None = None, to: str | None = None, zone_id: str | None = None,
                  format: str = "csv", db: Session = Depends(get_db)):
    q = db.query(Deviation)
    if zone_id:
        q = q.filter(Deviation.zone_id == zone_id)
    devs = q.all()

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["deviation_id", "type", "severity", "zone_id", "stage_id", "message", "risk", "created_at"])
    for d in devs:
        writer.writerow([d.deviation_id, d.type, d.severity, d.zone_id, d.stage_id, d.message, d.risk, d.created_at])

    buf.seek(0)
    filename = f"report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    return StreamingResponse(buf, media_type="text/csv",
                             headers={"Content-Disposition": f"attachment; filename={filename}"})