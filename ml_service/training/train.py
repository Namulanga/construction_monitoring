from ultralytics import YOLO
from pathlib import Path

DATA_YAML = Path("data/datasets/yolo/data.yaml")


def main():
    model = YOLO("yolov8n.pt")  # нано-версия, быстрая
    model.train(
        data=str(DATA_YAML),
        epochs=50,
        imgsz=640,
        batch=16,
        patience=10,
        project="ml_service/runs",
        name="baseline",
        exist_ok=True,
    )

    # Копируем лучшие веса в ml_service/weights/best.pt
    best = Path("ml_service/runs/baseline/weights/best.pt")
    if best.exists():
        target = Path("ml_service/weights/best.pt")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(best.read_bytes())
        print(f"weights copied → {target}")


if __name__ == "__main__":
    main()