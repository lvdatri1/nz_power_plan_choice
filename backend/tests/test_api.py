import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db import init_db, SessionLocal
from app.models import Retailer, Plan

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    init_db()
    db = SessionLocal()
    if db.query(Retailer).count() == 0:
        from app.seed_data import RETAILERS, PLANS_BY_RETAILER
        from app.models import PlanRateFlat, PlanRateTOU, PlanRateTOUExport
        for r in RETAILERS:
            db.add(Retailer(**r))
        db.flush()
        for retailer_name, plans in PLANS_BY_RETAILER:
            retailer = db.query(Retailer).filter(Retailer.name == retailer_name).first()
            if not retailer:
                continue
            for p in plans:
                plan = Plan(
                    retailer_id=retailer.id,
                    name=p["name"],
                    rate_type=p["rate_type"],
                    daily_charge=p["daily_charge"],
                    is_solar=p.get("is_solar", False),
                    has_export=p.get("has_export", False),
                    export_rate=p.get("export_rate"),
                    active=True,
                )
                db.add(plan)
                db.flush()
                if p["rate_type"].value == "FLAT":
                    for fr in p.get("flat_rates", []):
                        db.add(PlanRateFlat(plan_id=plan.id, **fr))
                if p["rate_type"].value == "TOU":
                    for tr in p.get("tou_rates", []):
                        db.add(PlanRateTOU(plan_id=plan.id, **tr))
                    for er in p.get("tou_export_rates", []):
                        db.add(PlanRateTOUExport(plan_id=plan.id, **er))
        db.commit()
    db.close()


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_list_retailers():
    r = client.get("/api/retailers")
    assert r.status_code == 200
    data = r.json()
    assert len(data) >= 10
    names = [d["name"] for d in data]
    assert "Contact Energy" in names
    assert "Meridian Energy" in names


def test_get_retailer():
    r = client.get("/api/retailers/1")
    assert r.status_code == 200
    assert r.json()["name"] == "Contact Energy"


def test_get_retailer_not_found():
    r = client.get("/api/retailers/999")
    assert r.status_code == 404


def test_list_plans():
    r = client.get("/api/plans")
    assert r.status_code == 200
    data = r.json()
    assert len(data) >= 20


def test_list_plans_filter_retailer():
    r = client.get("/api/plans?retailer_id=1")
    assert r.status_code == 200
    for p in r.json():
        assert p["retailer_id"] == 1


def test_list_plans_filter_rate_type():
    r = client.get("/api/plans?rate_type=TOU")
    assert r.status_code == 200
    for p in r.json():
        assert p["rate_type"] == "TOU"


def test_get_plan():
    r = client.get("/api/plans/1")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == 1
    assert "retailer" in data


def test_get_plan_not_found():
    r = client.get("/api/plans/999")
    assert r.status_code == 404


def test_calculate_cost_flat():
    r = client.post("/api/cost/calculate", json={
        "plan_id": 4,
        "usage": [{"timestamp": "2026-07-22T08:00:00", "kwh": 5.0}],
    })
    assert r.status_code == 200
    data = r.json()
    assert data["plan_name"] == "Standard Flat"
    assert data["rate_type"] == "FLAT"
    assert data["breakdown"]["import_cost"] == pytest.approx(1.45, rel=0.01)
    assert data["breakdown"]["daily_charges"] > 0


def test_calculate_cost_tou():
    r = client.post("/api/cost/calculate", json={
        "plan_id": 7,
        "usage": [
            {"timestamp": "2026-07-22T08:00:00", "kwh": 1.5},
            {"timestamp": "2026-07-22T21:30:00", "kwh": 2.0},
        ],
    })
    assert r.status_code == 200
    data = r.json()
    assert data["rate_type"] == "TOU"
    assert data["breakdown"]["import_cost"] == pytest.approx(0.525, rel=0.01)


def test_calculate_cost_with_export():
    r = client.post("/api/cost/calculate", json={
        "plan_id": 3,
        "usage": [{"timestamp": "2026-07-22T08:00:00", "kwh": 4.0}],
        "include_export": True,
        "export_usage": [{"timestamp": "2026-07-22T10:00:00", "kwh": 2.5}],
    })
    assert r.status_code == 200
    data = r.json()
    assert data["breakdown"]["export_credit"] > 0
    assert data["breakdown"]["import_cost"] > 0


def test_calculate_cost_invalid_plan():
    r = client.post("/api/cost/calculate", json={
        "plan_id": 999,
        "usage": [{"timestamp": "2026-07-22T08:00:00", "kwh": 1.0}],
    })
    assert r.status_code == 404
