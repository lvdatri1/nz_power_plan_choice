from __future__ import annotations

import logging
from datetime import timedelta, datetime
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy, CURRENCY_DOLLAR
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, CONF_PLAN_ID, CONF_IMPORT_SENSOR, CONF_EXPORT_SENSOR, SCAN_INTERVAL_SECONDS, SENSOR_PREFIX
from .data import get_plan_by_id
from .cost_engine import calculate_cost, minutes_from_midnight, day_of_week_group

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    config = entry.data
    plan_id = config[CONF_PLAN_ID]
    import_sensor_id = config.get(CONF_IMPORT_SENSOR, "sensor.energy_import_hourly")
    export_sensor_id = config.get(CONF_EXPORT_SENSOR, "sensor.energy_export_hourly")

    plan = get_plan_by_id(plan_id)
    if plan is None:
        _LOGGER.error("Plan %d not found in embedded data", plan_id)
        return

    coordinator = NZPowerCoordinator(hass, plan, import_sensor_id, export_sensor_id)
    await coordinator.async_refresh()

    async_add_entities([
        NZRateSensor(coordinator, plan_id),
        NZDailyCostSensor(coordinator, plan_id),
        NZMonthlyCostSensor(coordinator, plan_id),
        NZDailyImportSensor(coordinator, plan_id),
        NZDailyExportSensor(coordinator, plan_id),
        NZPlanInfoSensor(coordinator, plan_id),
    ])


class NZPowerCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, plan: dict, import_sensor_id: str, export_sensor_id: str) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="NZ Power Plans",
            update_interval=timedelta(seconds=SCAN_INTERVAL_SECONDS),
        )
        self.plan = plan
        self.import_sensor_id = import_sensor_id
        self.export_sensor_id = export_sensor_id

        self.current_rate: float = 0.0
        self.daily_import_kwh: float = 0.0
        self.daily_export_kwh: float = 0.0
        self.daily_import_cost: float = 0.0
        self.daily_export_credit: float = 0.0

    async def _async_update_data(self) -> dict[str, Any]:
        now = datetime.now()
        import_kwh = await self._read_sensor_kwh(self.import_sensor_id)
        export_kwh = await self._read_sensor_kwh(self.export_sensor_id) if self.export_sensor_id else 0.0

        if import_kwh is None:
            raise UpdateFailed("Import sensor not available")

        self.daily_import_kwh = import_kwh
        self.daily_export_kwh = export_kwh or 0.0

        breakdown = calculate_cost(self.plan, import_kwh, export_kwh or 0.0, days=1, now=now)
        self.daily_import_cost = breakdown["import_cost"]
        self.daily_export_credit = breakdown["export_credit"]
        self.current_rate = breakdown["import_cost"] / import_kwh if import_kwh else 0.0

        return {"import_kwh": import_kwh, "export_kwh": export_kwh}

    async def _read_sensor_kwh(self, entity_id: str) -> float | None:
        state = self.hass.states.get(entity_id)
        if state is None:
            return None
        try:
            return float(state.state)
        except (ValueError, TypeError):
            return None


class NZRateSensor(SensorEntity):
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_unit_of_measurement = CURRENCY_DOLLAR + "/kWh"
    _attr_icon = "mdi:currency-usd"
    _attr_should_poll = False

    def __init__(self, coordinator: NZPowerCoordinator, plan_id: int) -> None:
        self.coordinator = coordinator
        self._attr_unique_id = f"nz_power_current_rate_{plan_id}"
        self._attr_name = f"{SENSOR_PREFIX} Current Rate"

    @property
    def native_value(self) -> float:
        return round(self.coordinator.current_rate, 4)

    @property
    def extra_state_attributes(self) -> dict:
        plan = self.coordinator.plan
        return {
            "retailer": plan["retailer"],
            "plan": plan["name"],
            "rate_type": plan["rate_type"],
            "daily_charge": plan["daily_charge"],
        }

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))


class NZDailyCostSensor(SensorEntity):
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_unit_of_measurement = CURRENCY_DOLLAR
    _attr_icon = "mdi:cash"
    _attr_should_poll = False

    def __init__(self, coordinator: NZPowerCoordinator, plan_id: int) -> None:
        self.coordinator = coordinator
        self._attr_unique_id = f"nz_power_daily_cost_{plan_id}"
        self._attr_name = f"{SENSOR_PREFIX} Daily Cost"

    @property
    def native_value(self) -> float:
        return round(self.coordinator.daily_import_cost, 2)

    @property
    def extra_state_attributes(self) -> dict:
        return {
            "daily_charge": self.coordinator.plan["daily_charge"],
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

    def __init__(self, coordinator: NZPowerCoordinator, plan_id: int) -> None:
        self.coordinator = coordinator
        self._attr_unique_id = f"nz_power_monthly_cost_{plan_id}"
        self._attr_name = f"{SENSOR_PREFIX} Monthly Cost"

    @property
    def native_value(self) -> float:
        daily = self.coordinator.daily_import_cost + self.coordinator.plan["daily_charge"]
        return round(daily * 30, 2)

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))


class NZDailyImportSensor(SensorEntity):
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_icon = "mdi:transmission-tower-import"
    _attr_should_poll = False

    def __init__(self, coordinator: NZPowerCoordinator, plan_id: int) -> None:
        self.coordinator = coordinator
        self._attr_unique_id = f"nz_power_daily_import_{plan_id}"
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

    def __init__(self, coordinator: NZPowerCoordinator, plan_id: int) -> None:
        self.coordinator = coordinator
        self._attr_unique_id = f"nz_power_daily_export_{plan_id}"
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

    def __init__(self, coordinator: NZPowerCoordinator, plan_id: int) -> None:
        self.coordinator = coordinator
        self._attr_unique_id = f"nz_power_plan_info_{plan_id}"
        self._attr_name = f"{SENSOR_PREFIX} Plan Info"

    @property
    def native_value(self) -> str:
        plan = self.coordinator.plan
        return f"{plan['retailer']} - {plan['name']}"

    @property
    def extra_state_attributes(self) -> dict:
        plan = dict(self.coordinator.plan)
        plan.pop("tou_rates", None)
        plan.pop("tou_export_rates", None)
        return plan

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))
