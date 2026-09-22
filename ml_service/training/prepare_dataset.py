"""
Готовит единый YOLO-датасет из разных источников.
Раскладывает по data/datasets/yolo/{train,val}/{images,labels}.
Маппит сторонние названия классов в наши 8.
"""
import random
import shutil
from pathlib import Path

RAW = Path("data/datasets/raw")
OUT = Path("data/datasets/yolo")

CLASSES = [
    "excavator", "dump_truck", "crane", "bulldozer",
    "concrete_mixer", "roller", "truck", "crane_manipulator",
]
CLASS_MAP = {c: i for i, c in enumerate(CLASSES)}

# Синонимы из разных датасетов → наш класс
ALIASES = {
    "excavator": "excavator", "excavators": "excavator", "excavator_": "excavator",
    "dump_truck": "dump_truck", "dumper": "dump_truck", "truck_dump": "dump_truck",
    "crane": "crane", "cranes": "crane", "truck_crane": "crane",
    "bulldozer": "bulldozer", "bulldozers": "bulldozer", "dozer": "bulldozer",
    "concrete_mixer": "concrete_mixer", "mixer": "concrete_mixer", "cement_truck": "concrete_mixer",
    "roller": "roller", "road_roller": "roller",
    "truck": "truck", "lorry": "truck",
    "crane_manipulator": "crane_manipulator", "manipulator": "crane_manipulator",
}


def normalize(name: str) -> str | None:
    return ALIASES.get(name.lower().strip())


def collect_pairs():
    pairs = []
    for img in RAW.rglob("*.jpg"):
        lbl = img.with_suffix(".txt")
        if lbl.exists():
            pairs.append((img, lbl))
    for img in RAW.rglob("*.png"):
        lbl = img.with_suffix(".txt")
        if lbl.exists():
            pairs.append((img, lbl))
    return pairs


def split(pairs, val_ratio=0.2):
    random.seed(42)
    random.shuffle(pairs)
    n_val = int(len(pairs) * val_ratio)
    return pairs[n_val:], pairs[:n_val]


def convert_label(src: Path, dst: Path) -> bool:
    ok = False
    lines_out = []
    for line in src.read_text().splitlines():
        parts = line.split()
        if len(parts) < 5:
            continue
        cls_name = parts[0]
        mapped = normalize(cls_name) if cls_name.isalpha() else None
        # если первая колонка — индекс, а не имя, и у нас есть classes.txt, нужно
        # отдельно; здесь упрощение: пробуем по имени
        if mapped is None:
            continue
        idx = CLASS_MAP[mapped]
        lines_out.append(f"{idx} " + " ".join(parts[1:5]))
        ok = True
    if ok:
        dst.write_text("\n".join(lines_out))
    return ok


def main():
    for split_name in ("train", "val"):
        (OUT / split_name / "images").mkdir(parents=True, exist_ok=True)
        (OUT / split_name / "labels").mkdir(parents=True, exist_ok=True)

    pairs = collect_pairs()
    train, val = split(pairs)
    print(f"train: {len(train)}, val: {len(val)}")

    for split_name, subset in (("train", train), ("val", val)):
        count = 0
        for img, lbl in subset:
            dst_lbl = OUT / split_name / "labels" / lbl.name
            if convert_label(lbl, dst_lbl):
                dst_img = OUT / split_name / "images" / img.name
                shutil.copy(img, dst_img)
                count += 1
        print(f"{split_name}: {count} copied")

    # data.yaml
    yaml_path = OUT / "data.yaml"
    yaml_path.write_text(
        f"path: {OUT.resolve()}\n"
        f"train: train/images\n"
        f"val: val/images\n"
        f"nc: {len(CLASSES)}\n"
        f"names: {CLASSES}\n"
    )
    print(f"data.yaml saved: {yaml_path}")


if __name__ == "__main__":
    main()