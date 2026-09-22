import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Snapshot, Detection, Camera
from app.schemas.common import ListResponse
from app.schemas.snapshot import (
    SnapshotAnalysisOut, SnapshotDetailOut, DetectionOut, DeviationOut,
)
from app.services.ml_client import ml_client
from app.services.matching_engine import analyze_snapshot

router = APIRouter()


@router.post("", response_model=SnapshotAnalysisOut)
async def upload_snapshot(
    file: UploadFile = File(...),
    camera_id: str = Form(...),
    zone_id: str | None = Form(None),
    time: str | None = Form(None),
    db: Session = Depends(get_db),
):
    camera = db.get(Camera, camera_id)
    if not camera:
        raise HTTPException(404, f"Камера {camera_id} не найдена")
    zone_id = zone_id or camera.zone_id

    moment = datetime.fromisoformat(time) if time else datetime.utcnow()

    content = await file.read()
    if not content:
        raise HTTPException(400, "Пустой файл")

    # 1. Сохранить снимок
    snapshot_id = f"snap_{uuid.uuid4().hex[:10]}"
    storage = Path(settings.SNAPSHOT_STORAGE)
    storage.mkdir(parents=True, exist_ok=True)
    ext = Path(file.filename or "img.jpg").suffix or ".jpg"
    filepath = storage / f"{snapshot_id}{ext}"
    filepath.write_bytes(content)

    # 2. ML
    try:
        ml_result = ml_client.predict(content, file.filename or "image.jpg")
    except Exception as e:
        raise HTTPException(502, f"ML-сервис недоступен: {e}")

    # 3. Сохранить snapshot
    snapshot = Snapshot(
        snapshot_id=snapshot_id,
        camera_id=camera_id,
        zone_id=zone_id,
        stage_id=None,
        time=moment,
        image_url=str(filepath),
    )
    db.add(snapshot)

    # 4. Сохранить детекции
    for det in ml_result.get("detections", []):
        x, y, w, h = det["bbox"]
        db.add(Detection(
            snapshot_id=snapshot_id,
            equipment_id=det["class_name"],
            confidence=det["confidence"],
            x=x, y=y, w=w, h=h,
        ))
    db.commit()
    db.refresh(snapshot)

    # 5. Сопоставить
    deviations = analyze_snapshot(db, snapshot)

    return SnapshotAnalysisOut(
        snapshot_id=snapshot_id,
        zone_id=snapshot.zone_id,
        stage_id=snapshot.stage_id,
        detected_equipment=[
            DetectionOut(class_name=d.equipment_id, confidence=d.confidence,
                         bbox=[d.x, d.y, d.w, d.h])
            for d in snapshot.detections
        ],
        deviations=[DeviationOut.model_validate(d) for d in deviations],
    )


@router.get("", response_model=ListResponse)
def list_snapshots(
    zone_id: str | None = None,
    camera_id: str | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(Snapshot)
    if zone_id:
        q = q.filter(Snapshot.zone_id == zone_id)
    if camera_id:
        q = q.filter(Snapshot.camera_id == camera_id)
    items = q.order_by(Snapshot.time.desc()).limit(100).all()
    return ListResponse(items=[
        {"snapshot_id": s.snapshot_id, "camera_id": s.camera_id,
         "zone_id": s.zone_id, "time": s.time.isoformat(),
         "image_url": s.image_url}
        for s in items
    ])


@router.get("/{snapshot_id}", response_model=SnapshotDetailOut)
def get_snapshot(snapshot_id: str, db: Session = Depends(get_db)):
    s = db.get(Snapshot, snapshot_id)
    if not s:
        raise HTTPException(404, "Snapshot not found")
    return SnapshotDetailOut(
        snapshot_id=s.snapshot_id,
        camera_id=s.camera_id,
        zone_id=s.zone_id,
        stage_id=s.stage_id,
        time=s.time,
        image_url=s.image_url,
        detected_equipment=[
            DetectionOut(class_name=d.equipment_id, confidence=d.confidence,
                         bbox=[d.x, d.y, d.w, d.h])
            for d in s.detections
        ],
        deviations=[DeviationOut.model_validate(d) for d in s.deviations],
    )