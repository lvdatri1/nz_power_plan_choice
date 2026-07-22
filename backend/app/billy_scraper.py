import httpx
import re
import json
from typing import Any

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


def extract_rates_from_text(text: str) -> list[dict]:
    rates = []
    patterns = [
        (r"(\d+\.?\d*)\s*c?\s*per\s*kWh", "per_kwh"),
        (r"(\d+\.?\d*)\s*c\/kWh", "per_kwh"),
        (r"(\d+\.?\d*)\s*cents?\s*per\s*kWh", "per_kwh"),
        (r"(\d+\.?\d*)\s*cents?\s*\/\s*kWh", "per_kwh"),
        (r"buy.back.*?rate.*?(\d+\.?\d*)\s*c?\s*\/?\s*kWh", "buyback"),
        (r"export.*?rate.*?(\d+\.?\d*)\s*c?", "export"),
    ]
    for pattern, label in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            rate_val = float(m) / 100 if float(m) > 1 else float(m)
            rates.append({"label": label, "value": rate_val, "text": m})
    return rates


def extract_plan_names(text: str) -> list[str]:
    plan_keywords = ["Plan", "plan", "Saver", "Saver?"]
    plans = []
    lines = text.split("\n")
    for line in lines:
        for kw in plan_keywords:
            if kw in line and len(line) < 100:
                cleaned = line.strip().strip("-").strip("*").strip()
                if cleaned and cleaned not in plans:
                    plans.append(cleaned)
                break
    return plans


def parse_retailer_blocks(retailer: dict) -> dict:
    name = retailer.get("name", "")
    slug = retailer.get("slug", "")
    description = retailer.get("description", "")
    reference = retailer.get("reference", "")
    logo_url = ""
    if retailer.get("logo"):
        logo_url = f"https://billy.govt.nz{retailer['logo']['url']}"

    blocks = retailer.get("blocks", [])
    combined_text = description

    plan_names = []
    rates_found = []

    def process_content_blocks(content_blocks: list):
        for cb in content_blocks:
            if cb.get("blockType") == "richText":
                rich_text = cb.get("content", {})
                block_text = extract_text_from_rich_text(rich_text)
                nonlocal combined_text, rates_found, plan_names
                combined_text += "\n" + block_text
                rates_found.extend(extract_rates_from_text(block_text))
                plan_names.extend(extract_plan_names(block_text))
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
            rates_found.extend(extract_rates_from_text(block_text))
            plan_names.extend(extract_plan_names(block_text))

    info = {
        "name": name,
        "slug": slug,
        "reference": reference,
        "description": description,
        "logo_url": logo_url,
        "extracted_plan_names": list(set(plan_names)),
        "extracted_rates": rates_found,
        "raw_text_snippet": combined_text[:500],
    }
    return info


async def scrape_billy_retailers() -> list[dict]:
    retailers = await fetch_retailers()
    result = []
    for r in retailers:
        info = parse_retailer_blocks(r)
        result.append(info)
    return result


async def export_to_json(filepath: str = "data/billy_retailers.json"):
    data = await scrape_billy_retailers()
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Exported {len(data)} retailers to {filepath}")
    return data


if __name__ == "__main__":
    import asyncio
    asyncio.run(export_to_json())
