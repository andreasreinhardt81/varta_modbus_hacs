"""VARTA Modbus integration."""

from __future__ import annotations

from dataclasses import dataclass

from modbus_connection import ModbusTcpParams

from homeassistant.components.modbus import async_get_unit
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant

from .const import CONF_UNIT_ID, DOMAIN
from .coordinator import VartaCoordinator
from .vendor.varta_modbus import VartaStorage

PLATFORMS = [
    Platform.NUMBER,
    Platform.SENSOR,
]


@dataclass
class VartaRuntimeData:
    """Runtime data for one config entry."""

    device: VartaStorage
    coordinator: VartaCoordinator


type VartaConfigEntry = ConfigEntry[VartaRuntimeData]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: VartaConfigEntry,
) -> bool:
    """Set up VARTA Modbus from a config entry."""
    params = ModbusTcpParams(
        host=entry.data[CONF_HOST],
        port=entry.data[CONF_PORT],
    )

    unit = async_get_unit(
        hass,
        entry,
        params,
        entry.data[CONF_UNIT_ID],
    )

    device = VartaStorage(unit)
    coordinator = VartaCoordinator(hass, device)

    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = VartaRuntimeData(
        device=device,
        coordinator=coordinator,
    )

    await hass.config_entries.async_forward_entry_setups(
        entry,
        PLATFORMS,
    )

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: VartaConfigEntry,
) -> bool:
    """Unload a VARTA Modbus config entry."""
    return await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    )
