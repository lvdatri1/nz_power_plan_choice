# NZ Power Plans

Compare your home energy usage against real New Zealand electricity retailer plans — directly in Home Assistant. No external servers needed.

## Architecture

```
┌────────────────────────────────────────┐
│  Home Assistant (HACS Integration)     │
│                                        │
│  ┌──────────────┐  ┌────────────────┐  │
│  │ sensor.py    │  │ cost_engine.py  │  │
│  │ 6 sensors    │◀─│ FLAT / TOU calc │  │
│  └──────────────┘  └──────┬─────────┘  │
│                           │             │
│  ┌────────────────────────┘             │
│  │                                      │
│  ┌▼─────────────────────────────────┐   │
│  │ data.py (26 NZ plans embedded)   │   │
│  └──────────────────────────────────┘   │
└────────────────────────────────────────┘
```

## Backend (Optional)

For advanced usage, there's also a FastAPI backend in the `backend/` directory that provides the same calculations via REST API. You don't need it for the HA integration — all logic runs inside Home Assistant.

### Quick Start

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

### Docker

```bash
docker compose up -d
```

The backend auto-seeds 14 NZ retailers and 26 electricity plans on first run.

## Home Assistant Integration

### HACS Installation

1. Go to **HACS → Custom repositories**
2. Add `https://github.com/lvdatri1/nz_power_plan_choice` as an **Integration**
3. Click **Install**
4. Restart Home Assistant

### Manual Installation

Copy the `custom_components/nz_power_plans/` folder to your HA `config/custom_components/` directory:

```bash
cp -r custom_components/nz_power_plans/ /path/to/your/ha/config/custom_components/
```

Restart Home Assistant.

### Configuration

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **NZ Power Plans**
3. Select your **retailer** from the dropdown
4. Select your **plan** from the dropdown
5. Map your HA energy sensors:
   - Import sensor (e.g., `sensor.energy_import_hourly`)
   - Export sensor (e.g., `sensor.energy_export_hourly`)

### Sensors Created

| Sensor | Description |
|--------|-------------|
| `sensor.nz_power_current_rate` | Current effective rate ($/kWh) |
| `sensor.nz_power_daily_cost` | Estimated daily cost |
| `sensor.nz_power_monthly_cost` | Estimated monthly cost |
| `sensor.nz_power_daily_import` | Daily import kWh |
| `sensor.nz_power_daily_export` | Daily export kWh |
| `sensor.nz_power_plan_info` | Active plan details |

## Data Sources

The seed data includes plans from all 14 retailers on the NZ Electricity Authority's [billy.govt.nz](https://billy.govt.nz) comparison site:

- Contact Energy, Meridian Energy, Genesis Energy, Mercury NZ
- Electric Kiwi, 2degrees, Octopus Energy, Powershop
- Ecotricity, Pulse Energy, Nova Energy, Toast Electric
- Adonis Energy, Mystic Winds

Plans include FLAT and TOU (Time of Use) rate structures with peak/off-peak/free power windows and solar export rates.

## Rate Structures Supported

| Type | Description | Example |
|------|-------------|---------|
| **FLAT** | Single rate per kWh | 29c/kWh |
| **TIERED** | Progressive rates by usage band | First 100kWh @ 25c, next 200kWh @ 30c |
| **TOU** | Rates vary by time of day | Peak 35c, Off-peak 15c, Free 9pm-12am |

## Planned Features

- [ ] billy.govt.nz automated scraper (Playwright-based)
- [ ] EIEP14A standardized data format support (mandatory Oct 2026)
- [ ] Multi-plan comparison sensors
- [ ] Energy dashboard integration
- [ ] Forecast and anomaly detection

## Development

```bash
# Install dev dependencies
cd backend
pip install -r requirements-dev.txt

# Run tests
python3 -m pytest tests/ -v

# Run scraper
python3 -c "import asyncio; from app.billy_scraper import export_to_json; asyncio.run(export_to_json())"
```

## License

MIT
