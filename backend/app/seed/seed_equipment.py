from sqlalchemy.orm import Session
from app.models import Equipment

EQUIPMENT = [
    ("excavator", "Экскаватор", 0, "Гусеничный или колёсный экскаватор"),
    ("dump_truck", "Самосвал", 1, "Самосвал для вывоза грунта"),
    ("crane", "Автокран", 2, "Автомобильный кран"),
    ("bulldozer", "Бульдозер", 3, "Бульдозер для планировки"),
    ("concrete_mixer", "Бетоносмеситель", 4, "Автобетоносмеситель"),
    ("roller", "Каток", 5, "Дорожный каток"),
    ("truck", "Грузовик", 6, "Бортовой грузовик"),
    ("crane_manipulator", "Кран-манипулятор", 7, "КМУ"),
]


def run(db: Session):
    for eid, name, idx, desc in EQUIPMENT:
        if not db.get(Equipment, eid):
            db.add(Equipment(equipment_id=eid, name=name, class_index=idx, description=desc))
    db.commit()
    print(f"seed equipment: {len(EQUIPMENT)}")