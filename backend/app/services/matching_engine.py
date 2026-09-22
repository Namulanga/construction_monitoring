"""
Ядро: сопоставление фактических детекций с ожидаемой техникой по этапу.
"""
from datetime import datetime

from sqlalchemy.orm import Session

from app.models import (
    Snapshot, Schedule, StageEquipmentRule, Equipment, Stage, Zone, Deviation,
)
from app.services.anomaly_rules import classify_severity, build_message
from app.services.sri import compute_sri

import uuid


def find_active_stage(db: Session, zone_id: str | None, moment: datetime) -> Schedule | None:
    if not zone_id:
        return None
    return (
        db.query(Schedule)
        .filter(Schedule.zone_id == zone_id,
                Schedule.start_date <= moment.date(),
                Schedule.end_date >= moment.date())
        .order_by(Schedule.start_date.desc())
        .first()
    )


def analyze_snapshot(db: Session, snapshot: Snapshot) -> list[Deviation]:
    """
    Сравнивает детекции с правилами этапа. Создаёт Deviation и сохраняет.
    Возвращает список созданных отклонений.
    """
    schedule = find_active_stage(db, snapshot.zone_id, snapshot.time)
    if not schedule:
        return []
    snapshot.stage_id = schedule.stage_id

    rules = (
        db.query(StageEquipmentRule)
        .filter(StageEquipmentRule.stage_id == schedule.stage_id)
        .all()
    )
    required_ids = {r.equipment_id for r in rules if r.required}
    allowed_ids = {r.equipment_id for r in rules}
    min_count = {r.equipment_id: r.min_count for r in rules if r.required}

    # фактическое количество по классам
    detected_counts: dict[str, int] = {}
    for d in snapshot.detections:
        detected_counts[d.equipment_id] = detected_counts.get(d.equipment_id, 0) + 1

    detected_ids = set(detected_counts.keys())
    stage = db.get(Stage, schedule.stage_id)
    zone = db.get(Zone, snapshot.zone_id) if snapshot.zone_id else None
    stage_name = stage.name if stage else None
    zone_name = zone.name if zone else None

    deviations: list[Deviation] = []

    # 1. Отсутствующая обязательная техника
    missing = required_ids - detected_ids
    for eq_id in missing:
        eq = db.get(Equipment, eq_id)
        sev = classify_severity("missing_equipment", len(missing), len(required_ids))
        deviations.append(Deviation(
            deviation_id=f"dev_{uuid.uuid4().hex[:10]}",
            snapshot_id=snapshot.snapshot_id,
            stage_id=schedule.stage_id,
            zone_id=snapshot.zone_id,
            type="missing_equipment",
            expected=eq_id,
            actual=None,
            severity=sev,
            message=build_message("missing_equipment", stage_name, eq.name if eq else eq_id, zone_name),
            risk=0.0,
        ))

    # 2. Недостаточное количество
    for eq_id, mn in min_count.items():
        if eq_id in missing:
            continue
        if detected_counts.get(eq_id, 0) < mn:
            eq = db.get(Equipment, eq_id)
            deviations.append(Deviation(
                deviation_id=f"dev_{uuid.uuid4().hex[:10]}",
                snapshot_id=snapshot.snapshot_id,
                stage_id=schedule.stage_id,
                zone_id=snapshot.zone_id,
                type="insufficient_equipment",
                expected=f"{eq_id} >= {mn}",
                actual=f"{eq_id} = {detected_counts.get(eq_id, 0)}",
                severity="medium",
                message=build_message("insufficient_equipment", stage_name,
                                      eq.name if eq else eq_id, zone_name),
                risk=0.0,
            ))

    # 3. Лишняя техника
    unexpected = detected_ids - allowed_ids
    for eq_id in unexpected:
        eq = db.get(Equipment, eq_id)
        deviations.append(Deviation(
            deviation_id=f"dev_{uuid.uuid4().hex[:10]}",
            snapshot_id=snapshot.snapshot_id,
            stage_id=schedule.stage_id,
            zone_id=snapshot.zone_id,
            type="unexpected_equipment",
            expected=None,
            actual=eq_id,
            severity="low",
            message=build_message("unexpected_equipment", stage_name,
                                  eq.name if eq else eq_id, zone_name),
            risk=0.0,
        ))

    # SRI
    sri = compute_sri(deviations)
    for d in deviations:
        d.risk = sri

    for d in deviations:
        db.add(d)
    db.commit()
    return deviations