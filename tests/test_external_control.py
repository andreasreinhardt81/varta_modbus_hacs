"""Tests for VARTA external power control."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

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


async def test_watchdog_refreshes_active_limits():
    """Test watchdog periodically rewrites active discharge and charge limits."""
    battery = SimpleNamespace(write=AsyncMock())
    control = ExternalControl(battery)

    sleep_calls = 0

    async def fake_sleep(_interval: float) -> None:
        nonlocal sleep_calls
        sleep_calls += 1
        if sleep_calls > 1:
            raise asyncio.CancelledError

    with patch(
        "custom_components.varta_modbus.vendor.varta_modbus.external_control.asyncio.sleep",
        side_effect=fake_sleep,
    ):
        await control.async_set_discharging_power(-1000)
        await control.async_set_charging_power(1500)
        battery.write.reset_mock()

        assert control._task is not None
        await control._task

    assert battery.write.await_count == 2
    battery.write.assert_any_await("maximum_discharging_power", -1000)
    battery.write.assert_any_await("maximum_charging_power", 1500)

    await control.async_stop()


async def test_watchdog_continues_after_write_error():
    """Test watchdog logs errors and keeps running on refresh failure."""
    battery = SimpleNamespace(write=AsyncMock())
    control = ExternalControl(battery)

    sleep_calls = 0

    async def fake_sleep(_interval: float) -> None:
        nonlocal sleep_calls
        sleep_calls += 1
        if sleep_calls == 1:
            battery.write.side_effect = OSError("temporary failure")
            return
        raise asyncio.CancelledError

    with patch(
        "custom_components.varta_modbus.vendor.varta_modbus.external_control.asyncio.sleep",
        side_effect=fake_sleep,
    ):
        await control.async_set_charging_power(1000)
        assert control._task is not None
        await control._task

    assert battery.write.await_count == 2
    await control.async_stop()


async def test_stop_when_not_started():
    """Test calling async_stop when no watchdog task exists."""
    battery = SimpleNamespace(write=AsyncMock())
    control = ExternalControl(battery)

    await control.async_stop()

    assert not control.active
    assert control._task is None
