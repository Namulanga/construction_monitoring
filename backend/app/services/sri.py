"""
SRI — индекс риска срыва сроков.
Формула: сумма весов severity / нормировочный коэффициент.
Согласовать с аналитиком, пока базовая версия.
"""
from app.services.anomaly_rules import SEVERITY_WEIGHT


def compute_sri(deviations: list) -> float:
    if not deviations:
        return 0.0
    total = sum(SEVERITY_WEIGHT.get(d.severity, 1.0) for d in deviations)
    # нормируем в [0, 1]: 6+ баллов → 1.0
    return round(min(total / 6.0, 1.0), 2)