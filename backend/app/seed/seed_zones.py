from sqlalchemy.orm import Session
from app.models import Zone, Camera

ZONES = [
    ("zone_01", "Зона А — котлован", "Секция 1", "0"),
    ("zone_02", "Зона Б — фундамент", "Секция 1", "-1"),
    ("zone_03", "Зона В — надземная часть", "Секция 2", "1"),
]

CAMERAS = [
    ("cam_001", "zone_01", "Камера 1 — обзор котлована"),
    ("cam_002", "zone_02", "Камера 2 — фундамент"),
    ("cam_003", "zone_03", "Камера 3 — надземка"),
]


def run(db: Session):
    for zid, name, sec, fl in ZONES:
        if not db.get(Zone, zid):
            db.add(Zone(zone_id=zid, name=name, section=sec, floor=fl))
    for cid, zid, name in CAMERAS:
        if not db.get(Camera, cid):
            db.add(Camera(camera_id=cid, zone_id=zid, name=name))
    db.commit()
    print(f"seed zones: {len(ZONES)}, cameras: {len(CAMERAS)}")