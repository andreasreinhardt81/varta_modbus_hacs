"""Tests for VARTA external power control."""

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from custom_components.varta_modbus.vendor.varta_modbus.external_control import (
    ExternalControl,
)


@pytest.mark.parametrize(
    ("method_name", "register", "value"),
    [
        ("async_set_discharging_power", "maximum_discharging_power", -500),
        ("async_set_discharging_power", "maximum_discharging_power", -501),
        ("async_set_discharging_power", "maximum_discharging_power", 0),
        ("async_set_charging_power", "maximum_charging_power", 500),
        ("async_set_charging_power", "maximum_charging_power", 501),
        ("async_set_charging_power", "maximum_charging_power", 0),
    ],
)
async def test_accept_valid_power_limits(method_name, register, value):
    """Test valid values reach the VARTA battery register."""
    battery = SimpleNamespace(write=AsyncMock())
    control = ExternalControl(battery)

    await getattr(control, method_name)(value)

    battery.write.assert_awaited_once_with(register, value)
    assert control.active

    await control.async_stop()


@pytest.mark.parametrize(
    ("method_name", "value"),
    [
        ("async_set_discharging_power", -499),
        ("async_set_discharging_power", -1),
        ("async_set_charging_power", 1),
        ("async_set_charging_power", 498),
        ("async_set_charging_power", 499),
    ],
)
async def test_reject_invalid_power_limits(method_name, value):
    """Test values inside the forbidden range are rejected."""
    battery = SimpleNamespace(write=AsyncMock())
    control = ExternalControl(battery)

    with pytest.raises(ValueError):
        await getattr(control, method_name)(value)

    battery.write.assert_not_awaited()
    assert not control.active


async def test_failed_write_does_not_activate_external_control():
    """Test a failed Modbus write does not update watchdog state."""
    battery = SimpleNamespace(
        write=AsyncMock(side_effect=OSError("write failed"))
    )
    control = ExternalControl(battery)

    with pytest.raises(OSError, match="write failed"):
        await control.async_set_charging_power(500)

    assert not control.active
    assert control._task is None
