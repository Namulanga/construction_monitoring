from pydantic import BaseModel


class Detection(BaseModel):
    class_name: str
    confidence: float
    bbox: list[int]  # [x, y, w, h]


class PredictResponse(BaseModel):
    detections: list[Detection]
    image_size: list[int]  # [w, h]