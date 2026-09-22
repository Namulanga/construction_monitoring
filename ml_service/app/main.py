import io

from fastapi import FastAPI, UploadFile, File, HTTPException
from PIL import Image

from app.detector import Detector
from app.schemas import PredictResponse

app = FastAPI(title="ML Service — Construction Equipment Detection", version="0.1.0")
detector = Detector()


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": detector.model is not None}


@app.post("/predict", response_model=PredictResponse)
async def predict(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, "Ожидается изображение")
    data = await file.read()
    try:
        image = Image.open(io.BytesIO(data)).convert("RGB")
    except Exception as e:
        raise HTTPException(400, f"Не удалось открыть изображение: {e}")
    return detector.predict(image)