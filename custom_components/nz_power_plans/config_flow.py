from __future__ import annotations

from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, CONF_PLAN_ID, CONF_IMPORT_SENSOR, CONF_EXPORT_SENSOR
from .data import get_retailers, get_plans_by_retailer


class NZPowerPlansConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self):
        self._retailer: str | None = None
        self._data: dict = {}

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        retailers = get_retailers()
        retailer_options = {r: r for r in retailers}

        if user_input is not None:
            self._retailer = user_input["retailer"]
            return await self.async_step_plan()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("retailer"): vol.In(retailer_options),
            }),
        )

    async def async_step_plan(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        plans = get_plans_by_retailer(self._retailer)
        plan_options = {p["id"]: f"{p['name']} ({p['rate_type']})" for p in plans}

        if user_input is not None:
            self._data[CONF_PLAN_ID] = user_input[CONF_PLAN_ID]
            return await self.async_step_sensors()

        return self.async_show_form(
            step_id="plan",
            data_schema=vol.Schema({
                vol.Required("plan_id"): vol.In(plan_options),
            }),
        )

    async def async_step_sensors(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is not None:
            self._data.update(user_input)
            return self.async_create_entry(title="NZ Power Plans", data=self._data)

        return self.async_show_form(
            step_id="sensors",
            data_schema=vol.Schema({
                vol.Optional(CONF_IMPORT_SENSOR, default="sensor.energy_import_hourly"): str,
                vol.Optional(CONF_EXPORT_SENSOR, default="sensor.energy_export_hourly"): str,
            }),
        )
