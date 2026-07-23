from app.db import SessionLocal
from app.models import Retailer, Plan, PlanRateFlat, PlanRateTOU, PlanRateTOUExport, RateType


RETAILERS = [
    {"name": "Contact Energy", "slug": "contact-energy", "website": "https://contact.co.nz", "phone": "0800 224 424"},
    {"name": "Meridian Energy", "slug": "meridian-energy", "website": "https://meridianenergy.co.nz", "phone": "0800 496 496"},
    {"name": "Genesis Energy", "slug": "genesis-energy", "website": "https://genesisenergy.co.nz", "phone": "0800 300 400"},
    {"name": "Mercury NZ", "slug": "mercury-nz", "website": "https://mercury.co.nz", "phone": "0800 300 300"},
    {"name": "Electric Kiwi", "slug": "electric-kiwi", "website": "https://electrickiwi.co.nz", "phone": "0800 888 666"},
    {"name": "2degrees", "slug": "2degrees", "website": "https://2degrees.nz", "phone": "0800 022 022"},
    {"name": "Octopus Energy", "slug": "octopus-energy", "website": "https://octopusenergy.nz", "phone": "0800 888 284"},
    {"name": "Powershop", "slug": "powershop", "website": "https://powershop.co.nz", "phone": "0800 100 201"},
    {"name": "Ecotricity", "slug": "ecotricity", "website": "https://ecotricity.co.nz", "phone": "0800 888 123"},
    {"name": "Pulse Energy", "slug": "pulse-energy", "website": "https://pulseenergy.co.nz", "phone": "0800 785 733"},
    {"name": "Nova Energy", "slug": "nova-energy", "website": "https://novaenergy.co.nz", "phone": "0800 226 682"},
    {"name": "Toast Electric", "slug": "toast-electric", "website": "https://toastelectric.co.nz", "phone": "0800 486 278"},
    {"name": "Adonis Energy", "slug": "adonis-energy", "website": "https://adonisenergy.co.nz", "phone": "0800 236 647"},
    {"name": "Mystic Winds", "slug": "mystic-winds", "website": "https://mysticwinds.co.nz", "phone": ""},
]

CONTACT_PLANS = [
    {
        "name": "Good Nights",
        "rate_type": RateType.TOU,
        "daily_charge": 1.20, "is_solar": True, "has_export": True, "export_rate": 0.08,
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
        "name": "Good Weekends",
        "rate_type": RateType.TOU,
        "daily_charge": 1.20, "is_solar": True, "has_export": True, "export_rate": 0.08,
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
        "name": "Good Charge (EV)",
        "rate_type": RateType.TOU,
        "daily_charge": 1.50, "is_solar": True, "has_export": True, "export_rate": 0.12,
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
        "name": "Standard Flat", "rate_type": RateType.FLAT, "daily_charge": 0.95,
        "flat_rates": [{"rate_per_kwh": 0.29}],
    },
]

MERIDIAN_PLANS = [
    {
        "name": "Flat Rate", "rate_type": RateType.FLAT, "daily_charge": 0.90,
        "flat_rates": [{"rate_per_kwh": 0.28}],
    },
    {
        "name": "Time of Use", "rate_type": RateType.TOU,
        "daily_charge": 1.10, "is_solar": True, "has_export": True, "export_rate": 0.08,
        "tou_rates": [
            {"label": "Peak", "window_start": 420, "window_end": 600, "rate_per_kwh": 0.34, "days_of_week": "weekdays"},
            {"label": "Peak Evening", "window_start": 1020, "window_end": 1260, "rate_per_kwh": 0.32, "days_of_week": "weekdays"},
            {"label": "Off-Peak", "window_start": 0, "window_end": 420, "rate_per_kwh": 0.15, "days_of_week": "weekdays"},
            {"label": "Off-Peak Day", "window_start": 600, "window_end": 1020, "rate_per_kwh": 0.15, "days_of_week": "weekdays"},
            {"label": "Off-Peak Night", "window_start": 1260, "window_end": 1440, "rate_per_kwh": 0.15, "days_of_week": "weekdays"},
            {"label": "Weekend", "window_start": 0, "window_end": 1440, "rate_per_kwh": 0.14, "days_of_week": "weekends"},
        ],
    },
]

ELECTRIC_KIWI_PLANS = [
    {
        "name": "Kiwi Saver", "rate_type": RateType.TOU, "daily_charge": 1.05,
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
        "name": "MoveMaster", "rate_type": RateType.TOU, "daily_charge": 1.10,
        "is_solar": True, "has_export": True, "export_rate": 0.23,
        "tou_rates": [
            {"label": "Half Price Night", "window_start": 1260, "window_end": 1440, "rate_per_kwh": 0.08, "days_of_week": "all"},
            {"label": "Half Price Night", "window_start": 0, "window_end": 420, "rate_per_kwh": 0.08, "days_of_week": "all"},
            {"label": "Peak", "window_start": 420, "window_end": 600, "rate_per_kwh": 0.37, "days_of_week": "weekdays"},
            {"label": "Evening", "window_start": 1020, "window_end": 1260, "rate_per_kwh": 0.27, "days_of_week": "weekdays"},
            {"label": "Daytime", "window_start": 600, "window_end": 1020, "rate_per_kwh": 0.19, "days_of_week": "weekdays"},
            {"label": "Weekend", "window_start": 0, "window_end": 1440, "rate_per_kwh": 0.12, "days_of_week": "weekends"},
        ],
        "tou_export_rates": [],
    },
]

GENESIS_PLANS = [
    {
        "name": "Standard Flat", "rate_type": RateType.FLAT, "daily_charge": 0.85,
        "flat_rates": [{"rate_per_kwh": 0.30}],
    },
    {
        "name": "EV Plan", "rate_type": RateType.TOU,
        "daily_charge": 1.30, "is_solar": True, "has_export": True, "export_rate": 0.10,
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
        "name": "EVHome Plan", "rate_type": RateType.TOU,
        "daily_charge": 1.40, "is_solar": True, "has_export": True, "export_rate": 0.15,
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
]

MERCURY_PLANS = [
    {
        "name": "Standard Flat", "rate_type": RateType.FLAT, "daily_charge": 0.88,
        "flat_rates": [{"rate_per_kwh": 0.27}],
    },
    {
        "name": "Solar Plan", "rate_type": RateType.FLAT,
        "daily_charge": 0.95, "is_solar": True, "has_export": True, "export_rate": 0.11,
        "flat_rates": [{"rate_per_kwh": 0.26}],
    },
]

POWERSHOP_PLANS = [
    {
        "name": "Flat Rate", "rate_type": RateType.FLAT, "daily_charge": 0.82,
        "flat_rates": [{"rate_per_kwh": 0.28}],
    },
    {
        "name": "Solar Saver", "rate_type": RateType.TOU,
        "daily_charge": 1.00, "is_solar": True, "has_export": True, "export_rate": 0.13,
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
]

OCTOPUS_PLANS = [
    {
        "name": "Half Price Nights", "rate_type": RateType.TOU,
        "daily_charge": 1.15, "is_solar": True, "has_export": True, "export_rate": 0.10,
        "tou_rates": [
            {"label": "Half Price", "window_start": 1320, "window_end": 1440, "rate_per_kwh": 0.10, "days_of_week": "all"},
            {"label": "Half Price", "window_start": 0, "window_end": 420, "rate_per_kwh": 0.10, "days_of_week": "all"},
            {"label": "Peak", "window_start": 420, "window_end": 600, "rate_per_kwh": 0.35, "days_of_week": "weekdays"},
            {"label": "Evening", "window_start": 1020, "window_end": 1320, "rate_per_kwh": 0.28, "days_of_week": "weekdays"},
            {"label": "Daytime", "window_start": 600, "window_end": 1020, "rate_per_kwh": 0.18, "days_of_week": "weekdays"},
            {"label": "Weekend", "window_start": 420, "window_end": 1320, "rate_per_kwh": 0.14, "days_of_week": "weekends"},
        ],
        "tou_export_rates": [],
    },
    {
        "name": "Flat Rate", "rate_type": RateType.FLAT, "daily_charge": 0.85,
        "flat_rates": [{"rate_per_kwh": 0.26}],
    },
]

PULSE_PLANS = [
    {
        "name": "Power Shift", "rate_type": RateType.TOU,
        "daily_charge": 0.95, "is_solar": True, "has_export": True, "export_rate": 0.08,
        "tou_rates": [
            {"label": "Peak", "window_start": 420, "window_end": 600, "rate_per_kwh": 0.33, "days_of_week": "weekdays"},
            {"label": "Evening", "window_start": 1020, "window_end": 1260, "rate_per_kwh": 0.28, "days_of_week": "weekdays"},
            {"label": "Off-Peak", "window_start": 0, "window_end": 420, "rate_per_kwh": 0.14, "days_of_week": "weekdays"},
            {"label": "Daytime", "window_start": 600, "window_end": 1020, "rate_per_kwh": 0.16, "days_of_week": "weekdays"},
            {"label": "Night", "window_start": 1260, "window_end": 1440, "rate_per_kwh": 0.14, "days_of_week": "weekdays"},
            {"label": "Half Price Weekend", "window_start": 0, "window_end": 1440, "rate_per_kwh": 0.11, "days_of_week": "weekends"},
        ],
        "tou_export_rates": [],
    },
]

DEGREES_PLANS = [
    {
        "name": "Flat Rate", "rate_type": RateType.FLAT, "daily_charge": 0.80,
        "flat_rates": [{"rate_per_kwh": 0.29}],
    },
    {
        "name": "Broadband Bundle", "rate_type": RateType.FLAT,
        "daily_charge": 0.75, "flat_rates": [{"rate_per_kwh": 0.26}],
    },
]

ECOTRICITY_PLANS = [
    {
        "name": "Climate Positive Flat", "rate_type": RateType.FLAT,
        "daily_charge": 0.92, "flat_rates": [{"rate_per_kwh": 0.30}],
    },
]

NOVA_PLANS = [
    {
        "name": "Standard Flat", "rate_type": RateType.FLAT, "daily_charge": 0.88,
        "flat_rates": [{"rate_per_kwh": 0.29}],
    },
    {
        "name": "MultiSaver Bundle", "rate_type": RateType.FLAT,
        "daily_charge": 0.80, "flat_rates": [{"rate_per_kwh": 0.26}],
    },
]

TOAST_PLANS = [
    {
        "name": "Not-For-Profit Flat", "rate_type": RateType.FLAT,
        "daily_charge": 0.90, "flat_rates": [{"rate_per_kwh": 0.28}],
    },
]

ADONIS_PLANS = [
    {
        "name": "Flexi Flat", "rate_type": RateType.FLAT, "daily_charge": 0.85,
        "flat_rates": [{"rate_per_kwh": 0.27}],
    },
]

MYSTIC_PLANS = [
    {
        "name": "Simple Power", "rate_type": RateType.FLAT, "daily_charge": 0.75,
        "is_solar": True, "has_export": True, "export_rate": 0.10,
        "flat_rates": [{"rate_per_kwh": 0.25}],
    },
]

PLANS_BY_RETAILER = [
    ("Contact Energy", CONTACT_PLANS),
    ("Meridian Energy", MERIDIAN_PLANS),
    ("Electric Kiwi", ELECTRIC_KIWI_PLANS),
    ("Genesis Energy", GENESIS_PLANS),
    ("Mercury NZ", MERCURY_PLANS),
    ("Powershop", POWERSHOP_PLANS),
    ("Octopus Energy", OCTOPUS_PLANS),
    ("Pulse Energy", PULSE_PLANS),
    ("2degrees", DEGREES_PLANS),
    ("Ecotricity", ECOTRICITY_PLANS),
    ("Nova Energy", NOVA_PLANS),
    ("Toast Electric", TOAST_PLANS),
    ("Adonis Energy", ADONIS_PLANS),
    ("Mystic Winds", MYSTIC_PLANS),
]


def seed_if_empty():
    db = SessionLocal()
    try:
        if db.query(Retailer).count() > 0:
            return
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

                if p["rate_type"] == RateType.FLAT:
                    for fr in p.get("flat_rates", []):
                        db.add(PlanRateFlat(plan_id=plan.id, **fr))

                if p["rate_type"] == RateType.TOU:
                    for tr in p.get("tou_rates", []):
                        db.add(PlanRateTOU(plan_id=plan.id, **tr))
                    for er in p.get("tou_export_rates", []):
                        db.add(PlanRateTOUExport(plan_id=plan.id, **er))

        db.commit()
    finally:
        db.close()
