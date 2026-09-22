"""
Правила формирования аномалий и severity.
"""
SEVERITY_WEIGHT = {"low": 1.0, "medium": 2.0, "high": 3.0}


def classify_severity(dev_type: str, missing_count: int, required_count: int) -> str:
    """
    missing_count — сколько обязательной техники не хватает;
    required_count — сколько всего обязательно.
    """
    if dev_type == "missing_equipment":
        if required_count and missing_count / required_count >= 0.5:
            return "high"
        return "medium"
    if dev_type == "insufficient_equipment":
        return "medium"
    if dev_type == "unexpected_equipment":
        return "low"
    if dev_type == "delay":
        return "high"
    return "low"


def build_message(dev_type: str, stage_name: str | None, equipment_name: str | None,
                  zone_name: str | None) -> str:
    stage_part = f"этап «{stage_name}»" if stage_name else "текущий этап"
    zone_part = f"зона «{zone_name}»" if zone_name else "зона не определена"
    if dev_type == "missing_equipment":
        return f"На {stage_part} в {zone_part} отсутствует обязательная техника: {equipment_name}"
    if dev_type == "insufficient_equipment":
        return f"На {stage_part} в {zone_part} недостаточно техники: {equipment_name}"
    if dev_type == "unexpected_equipment":
        return f"На {stage_part} в {zone_part} обнаружена техника, не соответствующая этапу: {equipment_name}"
    if dev_type == "delay":
        return f"На {stage_part} в {zone_part} зафиксировано отклонение от графика"
    return f"Отклонение на {stage_part} в {zone_part}"