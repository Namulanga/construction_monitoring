from io import BytesIO
from PIL import Image

from app.seed import seed_equipment, seed_zones, seed_rules


def make_image():
    buf = BytesIO()
    Image.new("RGB", (640, 480), (128, 128, 128)).save(buf, format="JPEG")
    return buf.getvalue()


def test_upload_snapshot(client, db):
    seed_equipment.run(db)
    seed_zones.run(db)
    seed_rules.run(db)

    files = {"file": ("t.jpg", make_image(), "image/jpeg")}
    data = {"camera_id": "cam_001", "zone_id": "zone_01"}
    r = client.post("/api/v1/snapshots", files=files, data=data)
    assert r.status_code == 200
    body = r.json()
    assert "snapshot_id" in body
    assert isinstance(body["detected_equipment"], list)


def test_upload_snapshot_bad_camera(client):
    files = {"file": ("t.jpg", make_image(), "image/jpeg")}
    data = {"camera_id": "cam_999"}
    r = client.post("/api/v1/snapshots", files=files, data=data)
    assert r.status_code == 404


def test_upload_snapshot_empty(client):
    files = {"file": ("t.jpg", b"", "image/jpeg")}
    data = {"camera_id": "cam_001"}
    r = client.post("/api/v1/snapshots", files=files, data=data)
    assert r.status_code == 400