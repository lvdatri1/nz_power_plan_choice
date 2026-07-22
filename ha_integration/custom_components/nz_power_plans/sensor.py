from __future__ import annotations

import logging
from datetime import timedelta, datetime
from typing import Any

import httpx

from homeassistant.components.sensor import SensorEntity, SensorStateClass, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy, CURRENCY_DOLLAR
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    CONF_BACKEND_URL,
    CONF_PLAN_ID,
    CONF_IMPORT_SENSOR,
    CONF_EXPORT_SENSOR,
    SCAN_INTERVAL_SECONDS,
    SENSOR_PREFIX,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    config = entry.data
    backend_url = config[CONF_BACKEND_URL]
    plan_id = config[CONF_PLAN_ID]
    import_sensor_id = config.get(CONF_IMPORT_SENSOR, "sensor.energy_import")
    export_sensor_id = config.get(CONF_EXPORT_SENSOR, "sensor.energy_export")

    plan_info = await fetch_plan(backend_url, plan_id)
    if plan_info is None:
        _LOGGER.error("Cannot fetch plan %d from %s", plan_id, backend_url)
        return

    coordinator = NZPowerCoordinator(hass, backend_url, plan_id, plan_info, import_sensor_id, export_sensor_id)
    await coordinator.async_refresh()

    async_add_entities([
        NZRateSensor(coordinator),
        NZDailyCostSensor(coordinator),
        NZMonthlyCostSensor(coordinator),
        NZDailyImportSensor(coordinator),
        NZDailyExportSensor(coordinator),
        NZPlanInfoSensor(coordinator),
    ])


async def fetch_plan(url: str, plan_id: int) -> dict | None:
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{url}/api/plans/{plan_id}", timeout=10)
            if r.status_code == 200:
                return r.json()
    except Exception as e:
        _LOGGER.warning("fetch_plan error: %s", e)
    return None


class NZPowerCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, backend_url: str, plan_id: int,
                 plan_info: dict, import_sensor_id: str, export_sensor_id: str) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="NZ Power Plans",
            update_interval=timedelta(seconds=SCAN_INTERVAL_SECONDS),
        )
        self.backend_url = backend_url
        self.plan_id = plan_id
        self.plan_info = plan_info
        self.import_sensor_id = import_sensor_id
        self.export_sensor_id = export_sensor_id

        self.current_rate: float = 0.0
        self.daily_charge: float = plan_info.get("daily_charge", 0)
        self.daily_import_kwh: float = 0.0
        self.daily_export_kwh: float = 0.0
        self.daily_import_cost: float = 0.0
        self.daily_export_credit: float = 0.0
        self.retailer_name: str = (plan_info.get("retailer") or {}).get("name", "")
        self.rate_type: str = plan_info.get("rate_type", "")

    async def _async_update_data(self) -> dict[str, Any]:
        import_kwh = await self._read_sensor_kwh(self.import_sensor_id)
        export_kwh = await self._read_sensor_kwh(self.export_sensor_id) if self.export_sensor_id else 0.0

        if import_kwh is None:
            raise UpdateFailed("Import sensor not available")

        self.daily_import_kwh = import_kwh
        self.daily_export_kwh = export_kwh or 0.0

        usage = [{"timestamp": datetime.now().isoformat(), "kwh": import_kwh}]
        export_usage = [{"timestamp": datetime.now().isoformat(), "kwh": export_kwh or 0.0}] if export_kwh else []

        cost_data = await self._calculate_cost(usage, export_usage)
        if cost_data:
            breakdown = cost_data.get("breakdown", {})
            self.daily_import_cost = breakdown.get("import_cost", 0.0)
            self.daily_export_credit = breakdown.get("export_credit", 0.0)
            self.current_rate = breakdown.get("import_cost", 0.0) / import_kwh if import_kwh else 0.0

        return {"import_kwh": import_kwh, "export_kwh": export_kwh}

    async def _read_sensor_kwh(self, entity_id: str) -> float | None:
        state = self.hass.states.get(entity_id)
        if state is None:
            return None
        try:
            return float(state.state)
        except (ValueError, TypeError):
            return None

    async def _calculate_cost(self, usage: list, export_usage: list) -> dict | None:
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "plan_id": self.plan_id,
                    "usage": usage,
                    "include_export": bool(export_usage),
                    "export_usage": export_usage,
                }
                r = await client.post(f"{self.backend_url}/api/cost/calculate", json=payload, timeout=10)
                if r.status_code == 200:
                    return r.json()
        except Exception as e:
            _LOGGER.warning("Cost calculation error: %s", e)
        return None


class NZRateSensor(SensorEntity):
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_unit_of_measurement = CURRENCY_DOLLAR + "/kWh"
    _attr_icon = "mdi:currency-usd"
    _attr_should_poll = False

    def __init__(self, coordinator: NZPowerCoordinator) -> None:
        self.coordinator = coordinator
        self._attr_unique_id = f"nz_power_current_rate_{coordinator.plan_id}"
        self._attr_name = f"{SENSOR_PREFIX} Current Rate"

    @property
    def native_value(self) -> float:
        return round(self.coordinator.current_rate, 4)

    @property
    def extra_state_attributes(self) -> dict:
        return {
            "retailer": self.coordinator.retailer_name,
            "plan": self.coordinator.plan_info.get("name", ""),
            "rate_type": self.coordinator.rate_type,
            "daily_charge": self.coordinator.daily_charge,
        }

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))


class NZDailyCostSensor(SensorEntity):
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_unit_of_measurement = CURRENCY_DOLLAR
    _attr_icon = "mdi:cash"
    _attr_should_poll = False

    def __init__(self, coordinator: NZPowerCoordinator) -> None:
        self.coordinator = coordinator
        self._attr_unique_id = f"nz_power_daily_cost_{coordinator.plan_id}"
        self._attr_name = f"{SENSOR_PREFIX} Daily Cost"

    @property
    def native_value(self) -> float:
        return round(self.coordinator.daily_import_cost, 2)

    @property
    def extra_state_attributes(self) -> dict:
        return {
            "daily_charge": self.coordinator.daily_charge,
            "import_cost": round(self.coordinator.daily_import_cost, 2),
            "export_credit": round(self.coordinator.daily_export_credit, 2),
        }

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))


class NZMonthlyCostSensor(SensorEntity):
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_unit_of_measurement = CURRENCY_DOLLAR
    _attr_icon = "mdi:calendar-month"
    _attr_should_poll = False

    def __init__(self, coordinator: NZPowerCoordinator) -> None:
        self.coordinator = coordinator
        self._attr_unique_id = f"nz_power_monthly_cost_{coordinator.plan_id}"
        self._attr_name = f"{SENSOR_PREFIX} Monthly Cost"

    @property
    def native_value(self) -> float:
        return round(self.coordinator.daily_import_cost * 30 + self.coordinator.daily_charge * 30, 2)

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))


class NZDailyImportSensor(SensorEntity):
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_icon = "mdi:transmission-tower-import"
    _attr_should_poll = False

    def __init__(self, coordinator: NZPowerCoordinator) -> None:
        self.coordinator = coordinator
        self._attr_unique_id = f"nz_power_daily_import_{coordinator.plan_id}"
        self._attr_name = f"{SENSOR_PREFIX} Daily Import"

    @property
    def native_value(self) -> float:
        return round(self.coordinator.daily_import_kwh, 3)

    @property
    def extra_state_attributes(self) -> dict:
        return {"import_cost": round(self.coordinator.daily_import_cost, 2)}

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))


class NZDailyExportSensor(SensorEntity):
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_icon = "mdi:transmission-tower-export"
    _attr_should_poll = False

    def __init__(self, coordinator: NZPowerCoordinator) -> None:
        self.coordinator = coordinator
        self._attr_unique_id = f"nz_power_daily_export_{coordinator.plan_id}"
        self._attr_name = f"{SENSOR_PREFIX} Daily Export"

    @property
    def native_value(self) -> float:
        return round(self.coordinator.daily_export_kwh, 3)

    @property
    def extra_state_attributes(self) -> dict:
        return {"export_credit": round(self.coordinator.daily_export_credit, 2)}

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))


class NZPlanInfoSensor(SensorEntity):
    _attr_icon = "mdi:information"
    _attr_should_poll = False

    def __init__(self, coordinator: NZPowerCoordinator) -> None:
        self.coordinator = coordinator
        self._attr_unique_id = f"nz_power_plan_info_{coordinator.plan_id}"
        self._attr_name = f"{SENSOR_PREFIX} Plan Info"

    @property
    def native_value(self) -> str:
        return f"{self.coordinator.retailer_name} - {self.coordinator.plan_info.get('name', '')}"

    @property
    def extra_state_attributes(self) -> dict:
        info = dict(self.coordinator.plan_info) if self.coordinator.plan_info else {}
        info.pop("retailer", None)
        return info

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))
