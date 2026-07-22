from __future__ import annotations

from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, CONF_BACKEND_URL, CONF_PLAN_ID, CONF_IMPORT_SENSOR, CONF_EXPORT_SENSOR, DEFAULT_BACKEND_URL

SCHEMA_STEP_1 = vol.Schema({
    vol.Required(CONF_BACKEND_URL, default=DEFAULT_BACKEND_URL): str,
    vol.Required(CONF_PLAN_ID, default=1): int,
})

SCHEMA_STEP_2 = vol.Schema({
    vol.Optional(CONF_IMPORT_SENSOR, default="sensor.energy_import"): str,
    vol.Optional(CONF_EXPORT_SENSOR, default="sensor.energy_export"): str,
})


async def validate_url(hass: HomeAssistant, url: str) -> None:
    import httpx
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{url}/health", timeout=5)
            if r.status_code != 200:
                raise InvalidUrl("Backend not reachable")
    except httpx.RequestError as e:
        raise InvalidUrl(f"Cannot connect: {e}")


class InvalidUrl(HomeAssistantError):
    pass


class NZPowerPlansConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        errors = {}
        if user_input is not None:
            try:
                await validate_url(self.hass, user_input[CONF_BACKEND_URL])
            except InvalidUrl as e:
                errors["base"] = str(e)
            else:
                self._data = user_input
                return await self.async_step_sensors()

        return self.async_show_form(step_id="user", data_schema=SCHEMA_STEP_1, errors=errors)

    async def async_step_sensors(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is not None:
            self._data.update(user_input)
            return self.async_create_entry(title="NZ Power Plans", data=self._data)
        return self.async_show_form(step_id="sensors", data_schema=SCHEMA_STEP_2)
