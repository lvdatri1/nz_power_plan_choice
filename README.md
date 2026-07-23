# NZ Power Plans

NZ electricity plan comparison and cost analysis. Runs as a **Home Assistant add-on** or a **standalone API server**.

- 14 NZ retailers, 26 plans built-in (Contact, Meridian, Genesis, Electric Kiwi, etc.)
- TOU (Time of Use), Flat, and Tiered rate structures
- Solar export credit with time-of-use export rates
- No external dependencies — everything runs locally

## Web UI

Open `http://localhost:8080` (standalone) or **Open Web UI** in the HA add-on page.

- **Dashboard** — quick cost estimate + HA connection status
- **Plans** — browse all 26 plans, filter by retailer/rate type, click for rate details
- **Calculator** — enter hourly usage, add solar export, see cost breakdown
- **Compare** — compare monthly costs across plans, cheapest highlighted

## Installation

### As HA Add-on

1. Go to **Settings → Add-ons → Add-on Store**
2. Click **⋮ → Repositories**
3. Add `https://github.com/lvdatri1/nz_power_plan_choice`
4. Find **NZ Power Plans** in the store and install
5. Go to **Configuration** and set your plan ID and sensor entity IDs
6. Start the add-on
7. Open **Web UI** from the add-on page — use the dashboard to browse plans, calculate costs, and compare rates

### Standalone Docker

```bash
docker compose up -d
# API at http://localhost:8080
```

### Manual

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

## API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/api/retailers` | List all retailers |
| GET | `/api/plans` | List plans (filter: `retailer_id`, `rate_type`) |
| GET | `/api/plans/{id}` | Get plan details with rates |
| POST | `/api/cost/calculate` | Calculate cost for usage against a plan |
| GET | `/api/ha/status` | (Add-on) Check HA connection |
| GET | `/api/ha/cost` | (Add-on) Read HA sensors + calculate cost |

### Cost Calculation

```bash
curl -X POST http://localhost:8080/api/cost/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "plan_id": 7,
    "usage": [{"timestamp": "2026-07-22T08:00:00", "kwh": 1.5}],
    "include_export": true,
    "export_usage": [{"timestamp": "2026-07-22T10:00:00", "kwh": 2.5}]
  }'
```

## REST Sensor Setup (optional)

Add to `configuration.yaml` to pull data into HA:

```yaml
sensor:
  - platform: rest
    name: "NZ Power Cost"
    resource: "http://a0d7b954-nz-power-plans:8080/api/ha/cost"
    value_template: "{{ value_json.breakdown.net_cost }}"
    unit_of_measurement: "NZD"
    scan_interval: 300
    json_attributes:
      - import_kwh
      - export_kwh
      - breakdown
```

Replace `a0d7b954-nz-power-plans` with your add-on's slug-based hostname (visible in add-on network info).

## Rate Structures

| Type | Description |
|------|-------------|
| **FLAT** | Single rate per kWh |
| **TIERED** | Progressive rates by usage band |
| **TOU** | Peak/off-peak/free power windows with day-of-week matching |

## Data Sources

Plans from all 14 retailers on [billy.govt.nz](https://billy.govt.nz): Contact Energy, Meridian Energy, Genesis Energy, Mercury NZ, Electric Kiwi, 2degrees, Octopus Energy, Powershop, Ecotricity, Pulse Energy, Nova Energy, Toast Electric, Adonis Energy, Mystic Winds.

## License

MIT
