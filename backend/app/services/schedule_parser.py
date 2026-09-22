"""
Парсит CSV/Excel с перечнем работ и наполняет stage + schedule.
Ожидаемые колонки: код, название, дата начала, дата окончания, зона (опционально).
Если структура другая — адаптировать под фактический файл.
"""
import io
from datetime import date, datetime

import pandas as pd
from sqlalchemy.orm import Session

from app.models import Stage, Schedule, Zone


def _to_date(value) -> date | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return pd.to_datetime(value, dayfirst=True).date()
    except Exception:
        return None


def parse_schedule_file(content: bytes, filename: str, db: Session) -> dict:
    if filename.lower().endswith(".csv"):
        df = pd.read_csv(io.BytesIO(content))
    else:
        df = pd.read_excel(io.BytesIO(content))

    df.columns = [str(c).strip().lower() for c in df.columns]

    col_code = next((c for c in df.columns if "код" in c or "code" in c or c == "№ п/п"), None)
    col_name = next((c for c in df.columns if "назв" in c or "name" in c or "вид" in c), None)
    col_start = next((c for c in df.columns if "начал" in c or "start" in c), None)
    col_end = next((c for c in df.columns if "оконч" in c or "end" in c), None)

    if not col_name:
        raise ValueError("Не найдена колонка с названием работ")

    zones = db.query(Zone).all()
    default_zone = zones[0].zone_id if zones else None

    stages_created = 0
    schedules_created = 0

    for _, row in df.iterrows():
        name = str(row[col_name]).strip() if pd.notna(row[col_name]) else None
        if not name or name.lower() in ("nan", ""):
            continue

        code = str(row[col_code]).strip() if col_code and pd.notna(row[col_code]) else None
        stage_id = code or name[:40].lower().replace(" ", "_")

        start = _to_date(row[col_start]) if col_start else None
        end = _to_date(row[col_end]) if col_end else None

        if not db.get(Stage, stage_id):
            db.add(Stage(stage_id=stage_id, code=code, name=name, parent_code=None))
            stages_created += 1

        if start and end and default_zone:
            plan_id = f"plan_{stage_id}_{default_zone}"
            if not db.get(Schedule, plan_id):
                db.add(Schedule(
                    plan_id=plan_id, stage_id=stage_id, zone_id=default_zone,
                    start_date=start, end_date=end, status="planned",
                ))
                schedules_created += 1

    db.commit()
    return {"stages_created": stages_created, "schedules_created": schedules_created}