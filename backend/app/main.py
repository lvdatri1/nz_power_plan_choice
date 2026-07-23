import os
import httpx
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db, init_db
from app.models import Retailer, Plan, RateType, PlanRateFlat, PlanRateTier, PlanRateTOU, PlanRateTOUExport
from app.schemas import RetailerCreate, RetailerResponse, PlanCreate, PlanResponse, CostRequest, CostResponse
from app.cost_engine import calculate_cost
from app import seed_data

app = FastAPI(title=settings.api_title, version=settings.api_version)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()
    seed_data.seed_if_empty()


@app.get("/health")
def health():
    return {"status": "ok", "version": settings.api_version}


@app.get("/api/retailers", response_model=list[RetailerResponse])
def list_retailers(db: Session = Depends(get_db)):
    return db.query(Retailer).all()


@app.get("/api/retailers/{retailer_id}", response_model=RetailerResponse)
def get_retailer(retailer_id: int, db: Session = Depends(get_db)):
    retailer = db.query(Retailer).filter(Retailer.id == retailer_id).first()
    if not retailer:
        raise HTTPException(status_code=404, detail="Retailer not found")
    return retailer


@app.get("/api/plans", response_model=list[PlanResponse])
def list_plans(
    retailer_id: int = None,
    rate_type: str = None,
    solar: bool = None,
    active: bool = None,
    db: Session = Depends(get_db),
):
    q = db.query(Plan)
    if retailer_id:
        q = q.filter(Plan.retailer_id == retailer_id)
    if rate_type:
        q = q.filter(Plan.rate_type == rate_type)
    if solar is not None:
        q = q.filter(Plan.is_solar == solar)
    if active is not None:
        q = q.filter(Plan.active == active)
    return q.all()


@app.get("/api/plans/{plan_id}", response_model=PlanResponse)
def get_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


@app.post("/api/plans", response_model=PlanResponse)
def create_plan(data: PlanCreate, db: Session = Depends(get_db)):
    retailer = db.query(Retailer).filter(Retailer.id == data.retailer_id).first()
    if not retailer:
        raise HTTPException(status_code=404, detail="Retailer not found")
    plan = Plan(
        retailer_id=data.retailer_id,
        name=data.name,
        product_code=data.product_code,
        rate_type=data.rate_type,
        description=data.description,
        daily_charge=data.daily_charge,
        is_solar=data.is_solar,
        has_export=data.has_export,
        export_rate=data.export_rate,
        active=data.active,
    )
    db.add(plan)
    db.flush()

    if data.rate_type == "FLAT":
        for r in data.flat_rates:
            plan.flat_rates.append(PlanRateFlat(plan_id=plan.id, **r.model_dump()))

    if data.rate_type == "TIERED":
        for r in data.tier_rates:
            plan.tier_rates.append(PlanRateTier(plan_id=plan.id, **r.model_dump()))

    if data.rate_type == "TOU":
        for r in data.tou_rates:
            plan.tou_rates.append(PlanRateTOU(plan_id=plan.id, **r.model_dump()))
        for r in data.tou_export_rates:
            plan.tou_export_rates.append(PlanRateTOUExport(plan_id=plan.id, **r.model_dump()))

    db.commit()
    db.refresh(plan)
    return plan


@app.post("/api/cost/calculate", response_model=CostResponse)
def calculate_plan_cost(req: CostRequest, db: Session = Depends(get_db)):
    plan = db.query(Plan).filter(Plan.id == req.plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    breakdown = calculate_cost(plan, req)
    return CostResponse(
        plan_id=plan.id,
        plan_name=plan.name,
        retailer_name=plan.retailer.name,
        rate_type=plan.rate_type.value,
        breakdown=breakdown,
    )


@app.get("/api/ha/status")
async def ha_status():
    if not settings.ha_url or not settings.ha_token:
        return {"connected": False, "message": "HA not configured (not running as add-on)"}
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{settings.ha_url}/api/states/{settings.nz_import_sensor}",
                headers={"Authorization": f"Bearer {settings.ha_token}"},
                timeout=10,
            )
            return {"connected": r.status_code == 200, "sensor": settings.nz_import_sensor, "status": r.status_code}
    except Exception as e:
        return {"connected": False, "error": str(e)}


@app.get("/api/ha/cost")
async def ha_cost(db: Session = Depends(get_db)):
    if not settings.ha_url or not settings.ha_token:
        raise HTTPException(status_code=400, detail="HA not configured")
    plan = db.query(Plan).filter(Plan.id == settings.nz_plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail=f"Plan {settings.nz_plan_id} not found")

    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {settings.ha_token}"}

        import_state = await client.get(
            f"{settings.ha_url}/api/states/{settings.nz_import_sensor}",
            headers=headers, timeout=10,
        )
        import_kwh = 0.0
        if import_state.status_code == 200:
            try:
                import_kwh = float(import_state.json()["state"])
            except (ValueError, KeyError):
                pass

        export_kwh = 0.0
        if settings.nz_export_sensor:
            export_state = await client.get(
                f"{settings.ha_url}/api/states/{settings.nz_export_sensor}",
                headers=headers, timeout=10,
            )
            if export_state.status_code == 200:
                try:
                    export_kwh = float(export_state.json()["state"])
                except (ValueError, KeyError):
                    pass

    req = CostRequest(
        plan_id=plan.id,
        usage=[{"timestamp": datetime.utcnow().isoformat(), "kwh": import_kwh}],
        include_export=bool(export_kwh),
        export_usage=[{"timestamp": datetime.utcnow().isoformat(), "kwh": export_kwh}] if export_kwh else [],
    )
    breakdown = calculate_cost(plan, req)
    return {
        "plan_id": plan.id,
        "plan_name": plan.name,
        "retailer_name": plan.retailer.name,
        "rate_type": plan.rate_type.value,
        "import_kwh": import_kwh,
        "export_kwh": export_kwh,
        "breakdown": breakdown.model_dump() if hasattr(breakdown, "model_dump") else breakdown,
    }


static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
def serve_index():
    return FileResponse(os.path.join(static_dir, "index.html"))
