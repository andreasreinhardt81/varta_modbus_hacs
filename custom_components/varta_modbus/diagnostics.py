"""Diagnostics support for VARTA Modbus."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data

from . import VartaConfigEntry

REDACT_CONFIG = {
    "host",
}

REDACT_DEVICE = {
    "serial_number",
}


async def async_get_config_entry_diagnostics(
    hass,
    entry: VartaConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""

    coordinator = entry.runtime_data.coordinator
    device = entry.runtime_data.device

    diagnostics: dict[str, Any] = {
        "config_entry": async_redact_data(
            entry.as_dict(),
            REDACT_CONFIG,
        ),
        "coordinator": {
            "last_update_success": coordinator.last_update_success,
            "update_interval_seconds": (
                int(coordinator.update_interval.total_seconds())
                if coordinator.update_interval
                else None
            ),
        },
        "identity": {
            "serial_number": device.identity.serial_number,
            "software": device.identity.software,
            "ems_software": device.identity.ems_software,
            "ens_software": device.identity.ens_software,
            "table_version": device.identity.table_version,
            "installed_battery_modules": (
                device.identity.installed_battery_modules
            ),
        },
        "battery": {
            "state": (
                device.battery.state.name
                if device.battery.state is not None
                else None
            ),
            "active_power": device.battery.active_power,
            "charging_power": device.battery.charging_power,
            "discharging_power": device.battery.discharging_power,
            "apparent_power": device.battery.apparent_power,
            "state_of_charge": device.battery.state_of_charge,
            "ac_to_dc_energy": device.battery.ac_to_dc_energy,
            "installed_capacity": device.battery.installed_capacity,
            "maximum_discharging_power": (
                device.battery.maximum_discharging_power
            ),
            "maximum_charging_power": (
                device.battery.maximum_charging_power
            ),
        },
        "grid": {
            "power": device.grid.power,
        },
    }

    return async_redact_data(
        diagnostics,
        REDACT_DEVICE,
    )
