"""Config flow for VARTA Modbus."""

from __future__ import annotations

from typing import Any, override

import voluptuous as vol
from modbus_connection import ModbusError, ModbusTcpParams

from homeassistant.components.modbus import async_get_temporary_unit
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.exceptions import HomeAssistantError

from .const import (
    CONF_UNIT_ID,
    DEFAULT_PORT,
    DEFAULT_UNIT_ID,
    DOMAIN,
)
from .vendor.varta_modbus import VartaStorage


async def async_validate_input(
    hass,
    data: dict[str, Any],
) -> None:
    """Validate the configured endpoint and VARTA device."""

    params = ModbusTcpParams(
        host=data[CONF_HOST].strip(),
        port=data[CONF_PORT],
    )

    async with async_get_temporary_unit(
        hass,
        params,
        data[CONF_UNIT_ID],
    ) as unit:
        device = VartaStorage(unit)
        await device.async_validate()


def _build_schema(
    *,
    host: str = "",
    port: int = DEFAULT_PORT,
    unit_id: int = DEFAULT_UNIT_ID,
) -> vol.Schema:
    """Build configuration schema."""

    return vol.Schema(
        {
            vol.Required(
                CONF_HOST,
                default=host,
            ): str,
            vol.Required(
                CONF_PORT,
                default=port,
            ): vol.All(
                vol.Coerce(int),
                vol.Range(min=1, max=65535),
            ),
            vol.Required(
                CONF_UNIT_ID,
                default=unit_id,
            ): vol.All(
                vol.Coerce(int),
                vol.Range(min=1, max=247),
            ),
        }
    )


class VartaConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a VARTA Modbus config flow."""

    VERSION = 1

    @override
    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Handle the user step."""

        errors: dict[str, str] = {}

        if user_input is not None:
            user_input[CONF_HOST] = user_input[CONF_HOST].strip()

            self._async_abort_entries_match(
                {
                    CONF_HOST: user_input[CONF_HOST],
                    CONF_PORT: user_input[CONF_PORT],
                    CONF_UNIT_ID: user_input[CONF_UNIT_ID],
                }
            )

            try:
                await async_validate_input(
                    self.hass,
                    user_input,
                )
            except (
                ModbusError,
                HomeAssistantError,
                TimeoutError,
                ValueError,
            ):
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title="VARTA Modbus",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_build_schema(),
            errors=errors,
        )

    async def async_step_reconfigure(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Handle integration reconfiguration."""

        entry = self._get_reconfigure_entry()

        errors: dict[str, str] = {}

        if user_input is not None:
            user_input[CONF_HOST] = user_input[CONF_HOST].strip()

            try:
                await async_validate_input(
                    self.hass,
                    user_input,
                )
            except (
                ModbusError,
                HomeAssistantError,
                TimeoutError,
                ValueError,
            ):
                errors["base"] = "cannot_connect"
            else:
                return self.async_update_reload_and_abort(
                    entry,
                    data=user_input,
                )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=_build_schema(
                host=entry.data[CONF_HOST],
                port=entry.data[CONF_PORT],
                unit_id=entry.data[CONF_UNIT_ID],
            ),
            errors=errors,
        )
