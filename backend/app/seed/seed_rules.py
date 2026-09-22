from sqlalchemy.orm import Session
from app.models import Stage, StageEquipmentRule

# stage_id → [(equipment_id, required, min_count, max_count)]
RULES = {
    "prep_territory":   [("bulldozer", True, 1, 3), ("truck", True, 1, 3)],
    "demolition":       [("excavator", True, 1, 3), ("dump_truck", True, 2, 5)],
    "excavation":       [("excavator", True, 1, 3), ("dump_truck", True, 2, 5)],
    "piles":            [("crane", True, 1, 2), ("concrete_mixer", True, 1, 3)],
    "foundation":       [("concrete_mixer", True, 1, 3), ("crane", True, 1, 2)],
    "monolith":         [("concrete_mixer", True, 1, 3), ("crane", True, 1, 2)],
    "earthworks":       [("excavator", True, 1, 3), ("bulldozer", True, 1, 2), ("roller", True, 1, 2)],
    "road_pavement":    [("roller", True, 1, 2), ("truck", True, 1, 3)],
    "landscaping":      [("truck", True, 1, 2), ("crane_manipulator", False, 0, 2)],
}

STAGES = [
    ("prep_territory", "10", "Подготовка территории", None),
    ("demolition", "10.3", "Снос зданий", "10"),
    ("excavation", "12.3.1", "Устройство котлована", "12.3"),
    ("piles", "12.3.2", "Устройство свай", "12.3"),
    ("foundation", "12.3.4", "Устройство фундамента", "12.3"),
    ("monolith", "12.3.9", "Монолитные работы ниже отметки 0", "12.3"),
    ("earthworks", "12.3.7", "Земляные работы", "12.3"),
    ("road_pavement", "12.4.14", "Покрытие дорожной одежды", "12.4"),
    ("landscaping", "12.7", "Благоустройство территории", "12"),
]


def run(db: Session):
    for sid, code, name, parent in STAGES:
        if not db.get(Stage, sid):
            db.add(Stage(stage_id=sid, code=code, name=name, parent_code=parent))
    db.commit()

    created = 0
    for sid, rules in RULES.items():
        for eid, req, mn, mx in rules:
            exists = db.query(StageEquipmentRule).filter_by(stage_id=sid, equipment_id=eid).first()
            if not exists:
                db.add(StageEquipmentRule(
                    stage_id=sid, equipment_id=eid,
                    required=req, min_count=mn, max_count=mx,
                ))
                created += 1
    db.commit()
    print(f"seed stages: {len(STAGES)}, rules created: {created}")