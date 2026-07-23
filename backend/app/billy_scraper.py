import httpx
import re

from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import Retailer, Plan, PlanRateFlat, RateType

BILLY_API_BASE = "https://billy.govt.nz/api"


async def fetch_retailers() -> list[dict]:
    retailers = []
    async with httpx.AsyncClient() as client:
        page = 1
        while True:
            r = await client.get(f"{BILLY_API_BASE}/retailers?page={page}&limit=50", timeout=15)
            if r.status_code != 200:
                break
            data = r.json()
            retailers.extend(data.get("docs", []))
            if not data.get("hasNextPage"):
                break
            page += 1
    return retailers


def extract_text_from_rich_text(node) -> str:
    parts = []
    if isinstance(node, dict):
        if "text" in node and isinstance(node["text"], str):
            return node["text"]
        for key, value in node.items():
            if key in ("children", "contentBlocks"):
                if isinstance(value, list):
                    for child in value:
                        parts.append(extract_text_from_rich_text(child))
            elif isinstance(value, (dict, list)):
                parts.append(extract_text_from_rich_text(value))
    elif isinstance(node, list):
        for item in node:
            parts.append(extract_text_from_rich_text(item))
    return " ".join(p for p in parts if p)


def extract_rates(text: str) -> dict:
    result: dict = {"flat_rates": [], "export_rates": [], "daily_charge": None}

    dc = re.search(r"daily\s*(charge|fixed)\s*[:\-]?\s*\$?(\d+\.?\d*)", text, re.IGNORECASE)
    if dc:
        result["daily_charge"] = float(dc.group(2))

    flat_matches = re.findall(r"(\d+\.?\d*)\s*c(ents?)?\s*(per\s*)?kWh", text, re.IGNORECASE)
    seen = set()
    for m in flat_matches:
        val = float(m[0])
        if val > 1:
            val = val / 100
        key = round(val, 4)
        if key not in seen and val < 5:
            seen.add(key)
            result["flat_rates"].append(key)

    export_matches = re.findall(
        r"(export|buy.back|solar.*feed|sell|credit).*?(\d+\.?\d*)\s*c",
        text, re.IGNORECASE,
    )
    seen_export = set()
    for m in export_matches:
        val = float(m[1])
        if val > 1:
            val = val / 100
        key = round(val, 4)
        if key not in seen_export and val < 5:
            seen_export.add(key)
            result["export_rates"].append(key)

    export_rate_plain = re.search(
        r"(\d+\.?\d*)\s*c(ents?)?\s*(per\s*)?kWh.*?(export|solar|buy.back)",
        text, re.IGNORECASE,
    )
    if not result["export_rates"] and export_rate_plain:
        val = float(export_rate_plain.group(1))
        if val > 1:
            val = val / 100
        if val < 5:
            result["export_rates"].append(round(val, 4))

    return result


def parse_retailer_blocks(retailer: dict) -> dict:
    name = retailer.get("name", "")
    slug = retailer.get("slug", "")
    description = retailer.get("description", "")
    blocks = retailer.get("blocks", [])

    combined_text = description or ""

    def process_content_blocks(content_blocks: list):
        nonlocal combined_text
        for cb in content_blocks:
            if cb.get("blockType") == "richText":
                rich_text = cb.get("content", {})
                block_text = extract_text_from_rich_text(rich_text)
                combined_text += "\n" + block_text
            elif cb.get("contentBlocks"):
                process_content_blocks(cb["contentBlocks"])

    for block in blocks:
        bt = block.get("blockType", "")
        if bt == "content" and block.get("contentBlocks"):
            process_content_blocks(block["contentBlocks"])
        elif bt == "richText":
            rich_text = block.get("content", {})
            block_text = extract_text_from_rich_text(rich_text)
            combined_text += "\n" + block_text

    rates = extract_rates(combined_text)

    plan_names = set()
    lines = combined_text.split("\n")
    for line in lines:
        stripped = line.strip().strip("-*").strip()
        if stripped and any(kw in stripped for kw in ("Plan", "plan", "Saver", "Saver?")):
            if len(stripped) < 80:
                plan_names.add(stripped)

    return {
        "name": name,
        "slug": slug,
        "rates": rates,
        "plan_names": list(plan_names),
    }


async def sync_from_billy(db: Session) -> int:
    retailers = await fetch_retailers()
    plans_updated = 0

    for r in retailers:
        info = parse_retailer_blocks(r)
        billy_name = info["name"]
        slug = info["slug"]
        rates = info["rates"]

        existing = db.query(Retailer).filter(Retailer.slug == slug).first()
        if not existing:
            existing = db.query(Retailer).filter(Retailer.name == billy_name).first()
        if not existing:
            existing = Retailer(name=billy_name, slug=slug)
            db.add(existing)
            db.flush()
        else:
            if existing.slug != slug:
                existing.slug = slug

        if rates["flat_rates"]:
            avg_rate = sum(rates["flat_rates"]) / len(rates["flat_rates"])
            flat_plan_name = f"{billy_name} Flat Rate"

            plan = db.query(Plan).filter(
                Plan.retailer_id == existing.id, Plan.name == flat_plan_name,
            ).first()

            if not plan:
                plan = Plan(
                    retailer_id=existing.id, name=flat_plan_name,
                    rate_type=RateType.FLAT,
                    daily_charge=rates["daily_charge"] or 0.90,
                )
                db.add(plan)
                db.flush()
                plans_updated += 1
                db.add(PlanRateFlat(plan_id=plan.id, rate_per_kwh=round(avg_rate, 6)))

            if rates["daily_charge"] and plan.daily_charge != rates["daily_charge"]:
                plan.daily_charge = rates["daily_charge"]

        if rates["export_rates"]:
            export_rate = rates["export_rates"][0]
            name = f"{billy_name} Solar"
            plan = db.query(Plan).filter(
                Plan.retailer_id == existing.id, Plan.name == name,
            ).first()
            if not plan:
                plan = Plan(
                    retailer_id=existing.id, name=name,
                    rate_type=RateType.FLAT,
                    daily_charge=rates["daily_charge"] or 0.95,
                    has_export=True, export_rate=round(export_rate, 6),
                )
                db.add(plan)
                db.flush()
                plans_updated += 1
            else:
                plan.has_export = True
                plan.export_rate = round(export_rate, 6)

    db.commit()
    return plans_updated


async def refresh_plans(db: Session = None) -> bool:
    close = db is None
    if db is None:
        db = SessionLocal()
    try:
        count = await sync_from_billy(db)
        print(f"Billy sync: {count} plans added/updated")
        return True
    except Exception as e:
        print(f"Billy sync skipped (using seed data): {e}")
        return False
    finally:
        if close:
            db.close()
