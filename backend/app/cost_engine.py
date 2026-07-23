from datetime import datetime
from typing import Optional

from app.models import Plan, PlanRateFlat, PlanRateTier, PlanRateTOU, PlanRateTOUExport, RateType
from app.schemas import CostRequest, CostBreakdown, CostItem


def minutes_from_midnight(ts: datetime) -> int:
    return ts.hour * 60 + ts.minute


def day_of_week_group(ts: datetime) -> str:
    return "weekends" if ts.weekday() >= 5 else "weekdays"


def find_tou_rate(tou_rates: list[PlanRateTOU], ts: datetime) -> Optional[float]:
    mins = minutes_from_midnight(ts)
    dow = day_of_week_group(ts)
    for r in tou_rates:
        if r.window_start <= mins < r.window_end:
            if r.days_of_week in ("all", dow):
                return r.rate_per_kwh
    return None


def calculate_cost(plan: Plan, req: CostRequest) -> CostBreakdown:
    items: list[CostItem] = []
    total_import_cost = 0.0
    total_export_credit = 0.0
    total_days = 0

    if plan.rate_type == RateType.FLAT:
        rate = plan.flat_rates[0].rate_per_kwh if plan.flat_rates else 0
        total_kwh = sum(r.kwh for r in req.usage)
        total_import_cost = total_kwh * rate
        items.append(CostItem(label="Flat rate import", kwh=total_kwh, rate=rate, cost=total_import_cost))

    elif plan.rate_type == RateType.TIERED:
        sorted_tiers = sorted(plan.tier_rates, key=lambda t: t.tier_min_kwh)
        total_kwh = sum(r.kwh for r in req.usage)
        remaining = total_kwh
        for tier in sorted_tiers:
            tier_kwh = min(remaining, tier.tier_max_kwh - tier.tier_min_kwh)
            if tier_kwh > 0:
                cost = tier_kwh * tier.rate_per_kwh
                total_import_cost += cost
                items.append(CostItem(label=f"Tier {tier.tier_min_kwh}-{tier.tier_max_kwh}kWh", kwh=tier_kwh, rate=tier.rate_per_kwh, cost=cost))
                remaining -= tier_kwh
        if remaining > 0:
            last_tier = sorted_tiers[-1]
            cost = remaining * last_tier.rate_per_kwh
            total_import_cost += cost
            items.append(CostItem(label=f"Over {sorted_tiers[-1].tier_max_kwh}kWh", kwh=remaining, rate=last_tier.rate_per_kwh, cost=cost))

    elif plan.rate_type == RateType.TOU:
        for record in req.usage:
            ts = datetime.fromisoformat(record.timestamp)
            rate = find_tou_rate(plan.tou_rates, ts)
            if rate is None:
                rate = 0.0
            cost = record.kwh * rate
            total_import_cost += cost
        label = "TOU import"
        total_kwh = sum(r.kwh for r in req.usage)
        avg_rate = total_import_cost / total_kwh if total_kwh else 0
        items.append(CostItem(label=label, kwh=total_kwh, rate=round(avg_rate, 6), cost=total_import_cost))

    if req.days > 0:
        total_days = req.days
    else:
        timestamps = [datetime.fromisoformat(r.timestamp) for r in req.usage]
        if timestamps:
            date_range = set(ts.date() for ts in timestamps)
            total_days = len(date_range)

    daily_charges = total_days * plan.daily_charge

    if req.include_export and req.export_usage:
        export_rates = plan.tou_export_rates if plan.rate_type == RateType.TOU else []
        total_export_kwh = sum(r.kwh for r in req.export_usage)
        if export_rates:
            for record in req.export_usage:
                ts = datetime.fromisoformat(record.timestamp)
                rate = find_tou_rate(export_rates, ts)
                if rate is None:
                    rate = plan.export_rate or 0
                total_export_credit += record.kwh * rate
        else:
            rate = plan.export_rate or 0
            total_export_credit = total_export_kwh * rate
        if total_export_credit:
            items.append(CostItem(label="Export credit", kwh=total_export_kwh, rate=rate, cost=-total_export_credit))

    net_cost = total_import_cost + daily_charges - total_export_credit

    return CostBreakdown(
        import_cost=round(total_import_cost, 4),
        export_credit=round(total_export_credit, 4),
        daily_charges=round(daily_charges, 4),
        net_cost=round(net_cost, 4),
        total_days=total_days,
        items=items,
    )
