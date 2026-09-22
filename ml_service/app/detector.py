from pathlib import Path
from PIL import Image

CLASSES = [
    "excavator", "dump_truck", "crane", "bulldozer",
    "concrete_mixer", "roller", "truck", "crane_manipulator",
]

WEIGHTS = Path(__file__).resolve().parent.parent / "weights" / "best.pt"


class Detector:
    def __init__(self):
        self.model = None
        self._load()

    def _load(self):
        if not WEIGHTS.exists():
            print(f"[detector] weights not found: {WEIGHTS}, running in stub mode")
            return
        from ultralytics import YOLO
        self.model = YOLO(str(WEIGHTS))
        print(f"[detector] loaded weights: {WEIGHTS}")

    def predict(self, image: Image.Image, conf_threshold: float = 0.35):
        w, h = image.size
        if self.model is None:
            # Заглушка: возвращаем один экскаватор для проверки пайплайна
            return {
                "detections": [{
                    "class_name": "excavator",
                    "confidence": 0.9,
                    "bbox": [int(w * 0.2), int(h * 0.3), int(w * 0.3), int(h * 0.3)],
                }],
                "image_size": [w, h],
            }

        results = self.model.predict(image, conf=conf_threshold, verbose=False)
        detections = []
        for r in results:
            for box in r.boxes:
                cls_idx = int(box.cls.item())
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                detections.append({
                    "class_name": CLASSES[cls_idx] if cls_idx < len(CLASSES) else f"class_{cls_idx}",
                    "confidence": float(box.conf.item()),
                    "bbox": [int(x1), int(y1), int(x2 - x1), int(y2 - y1)],
                })
        return {"detections": detections, "image_size": [w, h]}