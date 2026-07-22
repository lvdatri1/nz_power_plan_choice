import pytest
from datetime import datetime
from app.cost_engine import minutes_from_midnight, day_of_week_group, find_tou_rate
from app.models import PlanRateTOU


def test_minutes_from_midnight():
    ts = datetime(2026, 7, 22, 8, 30)
    assert minutes_from_midnight(ts) == 510

    ts = datetime(2026, 7, 22, 0, 0)
    assert minutes_from_midnight(ts) == 0

    ts = datetime(2026, 7, 22, 23, 59)
    assert minutes_from_midnight(ts) == 1439


def test_day_of_week_group():
    wed = datetime(2026, 7, 22)
    assert day_of_week_group(wed) == "weekdays"

    sat = datetime(2026, 7, 25)
    assert day_of_week_group(sat) == "weekends"

    sun = datetime(2026, 7, 26)
    assert day_of_week_group(sun) == "weekends"

    mon = datetime(2026, 7, 27)
    assert day_of_week_group(mon) == "weekdays"


def test_find_tou_rate_basic():
    rates = [
        PlanRateTOU(window_start=420, window_end=600, rate_per_kwh=0.35, days_of_week="weekdays"),
        PlanRateTOU(window_start=0, window_end=420, rate_per_kwh=0.15, days_of_week="weekdays"),
    ]
    ts = datetime(2026, 7, 22, 8, 0)
    assert find_tou_rate(rates, ts) == 0.35

    ts = datetime(2026, 7, 22, 2, 0)
    assert find_tou_rate(rates, ts) == 0.15


def test_find_tou_rate_weekend():
    rates = [
        PlanRateTOU(window_start=420, window_end=600, rate_per_kwh=0.35, days_of_week="weekdays"),
        PlanRateTOU(window_start=0, window_end=1440, rate_per_kwh=0.12, days_of_week="weekends"),
    ]
    ts = datetime(2026, 7, 25, 8, 0)
    assert find_tou_rate(rates, ts) == 0.12

    ts = datetime(2026, 7, 22, 8, 0)
    assert find_tou_rate(rates, ts) == 0.35


def test_find_tou_rate_all_days():
    rates = [
        PlanRateTOU(window_start=1260, window_end=1320, rate_per_kwh=0.0, days_of_week="all"),
    ]
    ts = datetime(2026, 7, 22, 21, 15)
    assert find_tou_rate(rates, ts) == 0.0

    ts = datetime(2026, 7, 25, 21, 15)
    assert find_tou_rate(rates, ts) == 0.0


def test_find_tou_rate_no_match():
    rates = [
        PlanRateTOU(window_start=420, window_end=600, rate_per_kwh=0.35, days_of_week="weekdays"),
    ]
    ts = datetime(2026, 7, 22, 12, 0)
    assert find_tou_rate(rates, ts) is None


def test_find_tou_rate_edge_cases():
    rates = [
        PlanRateTOU(window_start=0, window_end=420, rate_per_kwh=0.15, days_of_week="weekdays"),
    ]
    ts = datetime(2026, 7, 22, 6, 59)
    assert find_tou_rate(rates, ts) == 0.15

    ts = datetime(2026, 7, 22, 7, 0)
    assert find_tou_rate(rates, ts) is None


class TestPlanRateTOU:
    pass
