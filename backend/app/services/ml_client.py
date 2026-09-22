import httpx

from app.config import settings


class MLClient:
    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or settings.ML_SERVICE_URL

    def predict(self, image_bytes: bytes, filename: str = "image.jpg") -> dict:
        files = {"file": (filename, image_bytes, "image/jpeg")}
        with httpx.Client(timeout=60.0) as client:
            r = client.post(f"{self.base_url}/predict", files=files)
            r.raise_for_status()
            return r.json()


ml_client = MLClient()