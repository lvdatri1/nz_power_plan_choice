PLANS = [
    {
        "id": 1,
        "retailer": "Contact Energy",
        "name": "Good Nights",
        "rate_type": "TOU",
        "daily_charge": 1.20,
        "is_solar": True, "has_export": True, "export_rate": 0.08,
        "tou_rates": [
            {"label": "Peak", "window_start": 420, "window_end": 600, "rate_per_kwh": 0.35, "days_of_week": "weekdays"},
            {"label": "Peak", "window_start": 1020, "window_end": 1260, "rate_per_kwh": 0.35, "days_of_week": "weekdays"},
            {"label": "Free Power", "window_start": 1260, "window_end": 1440, "rate_per_kwh": 0.0, "days_of_week": "weekdays"},
            {"label": "Off-Peak", "window_start": 0, "window_end": 420, "rate_per_kwh": 0.15, "days_of_week": "weekdays"},
            {"label": "All day", "window_start": 0, "window_end": 1440, "rate_per_kwh": 0.15, "days_of_week": "weekends"},
        ],
        "tou_export_rates": [],
    },
    {
        "id": 2, "retailer": "Contact Energy", "name": "Good Weekends",
        "rate_type": "TOU", "daily_charge": 1.20,
        "is_solar": True, "has_export": True, "export_rate": 0.08,
        "tou_rates": [
            {"label": "Peak", "window_start": 420, "window_end": 600, "rate_per_kwh": 0.35, "days_of_week": "weekdays"},
            {"label": "Peak", "window_start": 1020, "window_end": 1260, "rate_per_kwh": 0.35, "days_of_week": "weekdays"},
            {"label": "Off-Peak", "window_start": 0, "window_end": 420, "rate_per_kwh": 0.15, "days_of_week": "weekdays"},
            {"label": "Off-Peak", "window_start": 600, "window_end": 1020, "rate_per_kwh": 0.15, "days_of_week": "weekdays"},
            {"label": "Free Weekend", "window_start": 0, "window_end": 1440, "rate_per_kwh": 0.0, "days_of_week": "weekends"},
        ],
        "tou_export_rates": [
            {"label": "Peak Export", "window_start": 420, "window_end": 600, "rate_per_kwh": 0.15, "days_of_week": "weekdays"},
            {"label": "Peak Export", "window_start": 1080, "window_end": 1320, "rate_per_kwh": 0.15, "days_of_week": "weekdays"},
        ],
    },
    {
        "id": 3, "retailer": "Contact Energy", "name": "Good Charge (EV)",
        "rate_type": "TOU", "daily_charge": 1.50,
        "is_solar": True, "has_export": True, "export_rate": 0.12,
        "tou_rates": [
            {"label": "Peak", "window_start": 420, "window_end": 540, "rate_per_kwh": 0.39, "days_of_week": "weekdays"},
            {"label": "Evening Peak", "window_start": 1080, "window_end": 1320, "rate_per_kwh": 0.39, "days_of_week": "weekdays"},
            {"label": "Half Price", "window_start": 1260, "window_end": 1440, "rate_per_kwh": 0.10, "days_of_week": "weekdays"},
            {"label": "Half Price Night", "window_start": 0, "window_end": 420, "rate_per_kwh": 0.10, "days_of_week": "weekdays"},
            {"label": "Off-Peak Day", "window_start": 540, "window_end": 1080, "rate_per_kwh": 0.18, "days_of_week": "weekdays"},
            {"label": "Weekend", "window_start": 0, "window_end": 1440, "rate_per_kwh": 0.12, "days_of_week": "weekends"},
        ],
        "tou_export_rates": [
            {"label": "Peak Export", "window_start": 420, "window_end": 540, "rate_per_kwh": 0.19, "days_of_week": "weekdays"},
            {"label": "Peak Export", "window_start": 1080, "window_end": 1320, "rate_per_kwh": 0.19, "days_of_week": "weekdays"},
        ],
    },
    {
        "id": 4, "retailer": "Contact Energy", "name": "Standard Flat",
        "rate_type": "FLAT", "daily_charge": 0.95,
        "flat_rate_per_kwh": 0.29,
    },
    {
        "id": 5, "retailer": "Meridian Energy", "name": "Flat Rate",
        "rate_type": "FLAT", "daily_charge": 0.90,
        "flat_rate_per_kwh": 0.28,
    },
    {
        "id": 6, "retailer": "Meridian Energy", "name": "Time of Use",
        "rate_type": "TOU", "daily_charge": 1.10,
        "is_solar": True, "has_export": True, "export_rate": 0.08,
        "tou_rates": [
            {"label": "Peak", "window_start": 420, "window_end": 600, "rate_per_kwh": 0.34, "days_of_week": "weekdays"},
            {"label": "Peak Evening", "window_start": 1020, "window_end": 1260, "rate_per_kwh": 0.32, "days_of_week": "weekdays"},
            {"label": "Off-Peak", "window_start": 0, "window_end": 420, "rate_per_kwh": 0.15, "days_of_week": "weekdays"},
            {"label": "Off-Peak Day", "window_start": 600, "window_end": 1020, "rate_per_kwh": 0.15, "days_of_week": "weekdays"},
            {"label": "Off-Peak Night", "window_start": 1260, "window_end": 1440, "rate_per_kwh": 0.15, "days_of_week": "weekdays"},
            {"label": "Weekend", "window_start": 0, "window_end": 1440, "rate_per_kwh": 0.14, "days_of_week": "weekends"},
        ],
    },
    {
        "id": 7, "retailer": "Electric Kiwi", "name": "Kiwi Saver",
        "rate_type": "TOU", "daily_charge": 1.05,
        "tou_rates": [
            {"label": "Hour of Free Power", "window_start": 1260, "window_end": 1320, "rate_per_kwh": 0.0, "days_of_week": "all"},
            {"label": "Peak", "window_start": 420, "window_end": 600, "rate_per_kwh": 0.35, "days_of_week": "weekdays"},
            {"label": "Evening", "window_start": 1020, "window_end": 1260, "rate_per_kwh": 0.25, "days_of_week": "weekdays"},
            {"label": "Off-Peak", "window_start": 0, "window_end": 420, "rate_per_kwh": 0.16, "days_of_week": "weekdays"},
            {"label": "Daytime", "window_start": 600, "window_end": 1020, "rate_per_kwh": 0.18, "days_of_week": "weekdays"},
            {"label": "Weekend", "window_start": 0, "window_end": 1440, "rate_per_kwh": 0.16, "days_of_week": "weekends"},
        ],
    },
    {
        "id": 8, "retailer": "Electric Kiwi", "name": "MoveMaster",
        "rate_type": "TOU", "daily_charge": 1.10,
        "is_solar": True, "has_export": True, "export_rate": 0.23,
        "tou_rates": [
            {"label": "Half Price Night", "window_start": 1260, "window_end": 1440, "rate_per_kwh": 0.08, "days_of_week": "all"},
            {"label": "Half Price Night", "window_start": 0, "window_end": 420, "rate_per_kwh": 0.08, "days_of_week": "all"},
            {"label": "Peak", "window_start": 420, "window_end": 600, "rate_per_kwh": 0.37, "days_of_week": "weekdays"},
            {"label": "Evening", "window_start": 1020, "window_end": 1260, "rate_per_kwh": 0.27, "days_of_week": "weekdays"},
            {"label": "Daytime", "window_start": 600, "window_end": 1020, "rate_per_kwh": 0.19, "days_of_week": "weekdays"},
            {"label": "Weekend", "window_start": 0, "window_end": 1440, "rate_per_kwh": 0.12, "days_of_week": "weekends"},
        ],
    },
    {
        "id": 9, "retailer": "Genesis Energy", "name": "Standard Flat",
        "rate_type": "FLAT", "daily_charge": 0.85,
        "flat_rate_per_kwh": 0.30,
    },
    {
        "id": 10, "retailer": "Genesis Energy", "name": "EV Plan",
        "rate_type": "TOU", "daily_charge": 1.30,
        "is_solar": True, "has_export": True, "export_rate": 0.10,
        "tou_rates": [
            {"label": "Power Shout", "window_start": 1260, "window_end": 1320, "rate_per_kwh": 0.0, "days_of_week": "all"},
            {"label": "Peak", "window_start": 420, "window_end": 600, "rate_per_kwh": 0.37, "days_of_week": "weekdays"},
            {"label": "Evening", "window_start": 1020, "window_end": 1260, "rate_per_kwh": 0.30, "days_of_week": "weekdays"},
            {"label": "Off-Peak", "window_start": 0, "window_end": 420, "rate_per_kwh": 0.12, "days_of_week": "weekdays"},
            {"label": "Daytime", "window_start": 600, "window_end": 1020, "rate_per_kwh": 0.18, "days_of_week": "weekdays"},
            {"label": "Night", "window_start": 1320, "window_end": 1440, "rate_per_kwh": 0.12, "days_of_week": "weekdays"},
            {"label": "Weekend Off-Peak", "window_start": 0, "window_end": 1440, "rate_per_kwh": 0.12, "days_of_week": "weekends"},
        ],
    },
    {
        "id": 11, "retailer": "Genesis Energy", "name": "EVHome Plan",
        "rate_type": "TOU", "daily_charge": 1.40,
        "is_solar": True, "has_export": True, "export_rate": 0.15,
        "tou_rates": [
            {"label": "50% Discount", "window_start": 1380, "window_end": 1440, "rate_per_kwh": 0.09, "days_of_week": "all"},
            {"label": "50% Discount", "window_start": 0, "window_end": 360, "rate_per_kwh": 0.09, "days_of_week": "all"},
            {"label": "Peak", "window_start": 420, "window_end": 600, "rate_per_kwh": 0.38, "days_of_week": "weekdays"},
            {"label": "Evening", "window_start": 1020, "window_end": 1380, "rate_per_kwh": 0.32, "days_of_week": "weekdays"},
            {"label": "Daytime", "window_start": 600, "window_end": 1020, "rate_per_kwh": 0.18, "days_of_week": "weekdays"},
            {"label": "Weekend", "window_start": 360, "window_end": 1380, "rate_per_kwh": 0.14, "days_of_week": "weekends"},
        ],
        "tou_export_rates": [
            {"label": "Peak Export", "window_start": 420, "window_end": 600, "rate_per_kwh": 0.15, "days_of_week": "weekdays"},
            {"label": "Peak Export", "window_start": 1020, "window_end": 1260, "rate_per_kwh": 0.15, "days_of_week": "weekdays"},
        ],
    },
    {
        "id": 12, "retailer": "Mercury NZ", "name": "Standard Flat",
        "rate_type": "FLAT", "daily_charge": 0.88,
        "flat_rate_per_kwh": 0.27,
    },
    {
        "id": 13, "retailer": "Mercury NZ", "name": "Solar Plan",
        "rate_type": "FLAT", "daily_charge": 0.95,
        "is_solar": True, "has_export": True, "export_rate": 0.11,
        "flat_rate_per_kwh": 0.26,
    },
    {
        "id": 14, "retailer": "Powershop", "name": "Flat Rate",
        "rate_type": "FLAT", "daily_charge": 0.82,
        "flat_rate_per_kwh": 0.28,
    },
    {
        "id": 15, "retailer": "Powershop", "name": "Solar Saver",
        "rate_type": "TOU", "daily_charge": 1.00,
        "is_solar": True, "has_export": True, "export_rate": 0.13,
        "tou_rates": [
            {"label": "Peak", "window_start": 420, "window_end": 660, "rate_per_kwh": 0.33, "days_of_week": "weekdays"},
            {"label": "Evening", "window_start": 1020, "window_end": 1260, "rate_per_kwh": 0.30, "days_of_week": "weekdays"},
            {"label": "Off-Peak", "window_start": 0, "window_end": 420, "rate_per_kwh": 0.14, "days_of_week": "weekdays"},
            {"label": "Daytime", "window_start": 660, "window_end": 1020, "rate_per_kwh": 0.16, "days_of_week": "weekdays"},
            {"label": "Night", "window_start": 1260, "window_end": 1440, "rate_per_kwh": 0.14, "days_of_week": "weekdays"},
            {"label": "Weekend", "window_start": 0, "window_end": 1440, "rate_per_kwh": 0.13, "days_of_week": "weekends"},
        ],
        "tou_export_rates": [
            {"label": "Winter Peak Export", "window_start": 420, "window_end": 660, "rate_per_kwh": 0.23, "days_of_week": "weekdays"},
        ],
    },
    {
        "id": 16, "retailer": "Octopus Energy", "name": "Half Price Nights",
        "rate_type": "TOU", "daily_charge": 1.15,
        "is_solar": True, "has_export": True, "export_rate": 0.10,
        "tou_rates": [
            {"label": "Half Price", "window_start": 1320, "window_end": 1440, "rate_per_kwh": 0.10, "days_of_week": "all"},
            {"label": "Half Price", "window_start": 0, "window_end": 420, "rate_per_kwh": 0.10, "days_of_week": "all"},
            {"label": "Peak", "window_start": 420, "window_end": 600, "rate_per_kwh": 0.35, "days_of_week": "weekdays"},
            {"label": "Evening", "window_start": 1020, "window_end": 1320, "rate_per_kwh": 0.28, "days_of_week": "weekdays"},
            {"label": "Daytime", "window_start": 600, "window_end": 1020, "rate_per_kwh": 0.18, "days_of_week": "weekdays"},
            {"label": "Weekend", "window_start": 420, "window_end": 1320, "rate_per_kwh": 0.14, "days_of_week": "weekends"},
        ],
    },
    {
        "id": 17, "retailer": "Octopus Energy", "name": "Flat Rate",
        "rate_type": "FLAT", "daily_charge": 0.85,
        "flat_rate_per_kwh": 0.26,
    },
    {
        "id": 18, "retailer": "Pulse Energy", "name": "Power Shift",
        "rate_type": "TOU", "daily_charge": 0.95,
        "is_solar": True, "has_export": True, "export_rate": 0.08,
        "tou_rates": [
            {"label": "Peak", "window_start": 420, "window_end": 600, "rate_per_kwh": 0.33, "days_of_week": "weekdays"},
            {"label": "Evening", "window_start": 1020, "window_end": 1260, "rate_per_kwh": 0.28, "days_of_week": "weekdays"},
            {"label": "Off-Peak", "window_start": 0, "window_end": 420, "rate_per_kwh": 0.14, "days_of_week": "weekdays"},
            {"label": "Daytime", "window_start": 600, "window_end": 1020, "rate_per_kwh": 0.16, "days_of_week": "weekdays"},
            {"label": "Night", "window_start": 1260, "window_end": 1440, "rate_per_kwh": 0.14, "days_of_week": "weekdays"},
            {"label": "Half Price Weekend", "window_start": 0, "window_end": 1440, "rate_per_kwh": 0.11, "days_of_week": "weekends"},
        ],
    },
    {
        "id": 19, "retailer": "2degrees", "name": "Flat Rate",
        "rate_type": "FLAT", "daily_charge": 0.80,
        "flat_rate_per_kwh": 0.29,
    },
    {
        "id": 20, "retailer": "2degrees", "name": "Broadband Bundle",
        "rate_type": "FLAT", "daily_charge": 0.75,
        "flat_rate_per_kwh": 0.26,
    },
    {
        "id": 21, "retailer": "Ecotricity", "name": "Climate Positive Flat",
        "rate_type": "FLAT", "daily_charge": 0.92,
        "flat_rate_per_kwh": 0.30,
    },
    {
        "id": 22, "retailer": "Nova Energy", "name": "Standard Flat",
        "rate_type": "FLAT", "daily_charge": 0.88,
        "flat_rate_per_kwh": 0.29,
    },
    {
        "id": 23, "retailer": "Nova Energy", "name": "MultiSaver Bundle",
        "rate_type": "FLAT", "daily_charge": 0.80,
        "flat_rate_per_kwh": 0.26,
    },
    {
        "id": 24, "retailer": "Toast Electric", "name": "Not-For-Profit Flat",
        "rate_type": "FLAT", "daily_charge": 0.90,
        "flat_rate_per_kwh": 0.28,
    },
    {
        "id": 25, "retailer": "Adonis Energy", "name": "Flexi Flat",
        "rate_type": "FLAT", "daily_charge": 0.85,
        "flat_rate_per_kwh": 0.27,
    },
    {
        "id": 26, "retailer": "Mystic Winds", "name": "Simple Power",
        "rate_type": "FLAT", "daily_charge": 0.75,
        "is_solar": True, "has_export": True, "export_rate": 0.10,
        "flat_rate_per_kwh": 0.25,
    },
]


def get_retailers() -> list[str]:
    seen = set()
    result = []
    for p in PLANS:
        if p["retailer"] not in seen:
            seen.add(p["retailer"])
            result.append(p["retailer"])
    return result


def get_plans_by_retailer(retailer: str) -> list[dict]:
    return [p for p in PLANS if p["retailer"] == retailer]


def get_plan_by_id(plan_id: int) -> dict | None:
    for p in PLANS:
        if p["id"] == plan_id:
            return p
    return None
