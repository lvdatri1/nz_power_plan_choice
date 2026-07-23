from __future__ import annotations

from datetime import datetime


def minutes_from_midnight(ts: datetime) -> int:
    return ts.hour * 60 + ts.minute


def day_of_week_group(ts: datetime) -> str:
    return "weekends" if ts.weekday() >= 5 else "weekdays"


def find_tou_rate(tou_rates: list[dict], ts: datetime) -> float | None:
    mins = minutes_from_midnight(ts)
    dow = day_of_week_group(ts)
    for r in tou_rates:
        if r["window_start"] <= mins < r["window_end"]:
            if r["days_of_week"] in ("all", dow):
                return r["rate_per_kwh"]
    return None


def calculate_import_cost(plan: dict, total_kwh: float, timestamp: datetime | None = None) -> float:
    rate_type = plan["rate_type"]
    if rate_type == "FLAT":
        return total_kwh * plan["flat_rate_per_kwh"]
    elif rate_type == "TOU":
        rate = 0.0
        if timestamp:
            found = find_tou_rate(plan.get("tou_rates", []), timestamp)
            if found is not None:
                rate = found
        return total_kwh * rate
    return 0.0


def calculate_export_credit(plan: dict, total_kwh: float, timestamp: datetime | None = None) -> float:
    export_rates = plan.get("tou_export_rates", [])
    if export_rates and timestamp:
        rate = find_tou_rate(export_rates, timestamp)
        if rate is None:
            rate = plan.get("export_rate", 0.0)
        return total_kwh * rate
    return total_kwh * plan.get("export_rate", 0.0)


def calculate_cost(plan: dict, import_kwh: float, export_kwh: float = 0.0,
                   days: int = 1, now: datetime | None = None) -> dict:
    if now is None:
        now = datetime.now()

    import_cost = calculate_import_cost(plan, import_kwh, now)
    export_credit = calculate_export_credit(plan, export_kwh, now) if export_kwh else 0.0
    daily_charges = days * plan["daily_charge"]
    net_cost = import_cost + daily_charges - export_credit

    return {
        "import_cost": round(import_cost, 4),
        "export_credit": round(export_credit, 4),
        "daily_charges": round(daily_charges, 4),
        "net_cost": round(net_cost, 4),
        "total_days": days,
    }
