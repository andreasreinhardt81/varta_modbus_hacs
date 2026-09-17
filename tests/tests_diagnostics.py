"""Diagnostics tests for VARTA Modbus."""

from types import SimpleNamespace

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.varta_modbus.const import DOMAIN
from custom_components.varta_modbus.diagnostics import (
    async_get_config_entry_diagnostics,
)


async def test_diagnostics_redacts_sensitive_data(hass):
    """Test diagnostics redacts host and serial number."""

    coordinator = SimpleNamespace(
        last_update_success=True,
        update_interval=None,
    )

    device = SimpleNamespace(
        identity=SimpleNamespace(
            serial_number="VARTA123456",
            software="1.0.0",
            ems_software="1.0.0",
            ens_software="1.0.0",
            table_version=12,
            installed_battery_modules=4,
            timestamp=123456789,
        ),
        battery=SimpleNamespace(
            state=SimpleNamespace(name="RUN"),
            active_power=100,
            charging_power=100,
            discharging_power=0,
            apparent_power=120,
            state_of_charge=85,
            ac_to_dc_energy=10000,
            installed_capacity=13500,
            maximum_discharging_power=-5000,
            maximum_charging_power=5000,
        ),
        grid=SimpleNamespace(
            power=-300,
        ),
    )

    entry = MockConfigEntry(
        domain=DOMAIN,
        title="VARTA Modbus",
        data={
            "host": "192.168.1.200",
            "port": 502,
            "unit_id": 1,
        },
    )

    entry.add_to_hass(hass)

    entry.runtime_data = SimpleNamespace(
        coordinator=coordinator,
        device=device,
    )

    diagnostics = await async_get_config_entry_diagnostics(
        hass,
        entry,
    )

    assert diagnostics["config_entry"]["data"]["host"] == "**REDACTED**"

    assert (
        diagnostics["identity"]["serial_number"]
        == "**REDACTED**"
    )

    assert diagnostics["battery"]["state"] == "RUN"

    assert diagnostics["battery"]["state_of_charge"] == 85

    assert diagnostics["grid"]["power"] == -300


async def test_diagnostics_contains_expected_sections(hass):
    """Test diagnostics structure."""

    coordinator = SimpleNamespace(
        last_update_success=True,
        update_interval=None,
    )

    device = SimpleNamespace(
        identity=SimpleNamespace(
            serial_number="ABC123",
            software="1.0.0",
            ems_software="1.0.0",
            ens_software="1.0.0",
            table_version=1,
            installed_battery_modules=1,
            timestamp=1,
        ),
        battery=SimpleNamespace(
            state=None,
            active_power=None,
            charging_power=None,
            discharging_power=None,
            apparent_power=None,
            state_of_charge=None,
            ac_to_dc_energy=None,
            installed_capacity=None,
            maximum_discharging_power=None,
            maximum_charging_power=None,
        ),
        grid=SimpleNamespace(
            power=None,
        ),
    )

    entry = MockConfigEntry(
        domain=DOMAIN,
        title="VARTA Modbus",
        data={
            "host": "192.168.1.10",
            "port": 502,
            "unit_id": 1,
        },
    )

    entry.add_to_hass(hass)

    entry.runtime_data = SimpleNamespace(
        coordinator=coordinator,
        device=device,
    )

    diagnostics = await async_get_config_entry_diagnostics(
        hass,
        entry,
    )

    assert "config_entry" in diagnostics
    assert "coordinator" in diagnostics
    assert "identity" in diagnostics
    assert "battery" in diagnostics
    assert "grid" in diagnostics
