"""Tests for VARTA Modbus number entities."""

from types import SimpleNamespace
from unittest.mock import AsyncMock

from custom_components.varta_modbus.number import (
    NUMBERS,
    VartaNumber,
)


def _create_device():
    """Create test device."""

    battery = SimpleNamespace(
        maximum_discharging_power=-5000,
        maximum_charging_power=4500,
        write=AsyncMock(),
    )

    return SimpleNamespace(
        identity=SimpleNamespace(
            serial_number="VARTA123",
            software="1.0.0",
        ),
        battery=battery,
    )


def _create_entry():
    """Create fake config entry."""

    return SimpleNamespace(
        entry_id="test_entry",
    )


def _create_coordinator(device):
    """Create fake coordinator."""

    return SimpleNamespace(
        device=device,
        async_request_refresh=AsyncMock(),
    )


def _create_number(key: str):
    """Create number entity."""

    device = _create_device()

    description = next(
        number
        for number in NUMBERS
        if number.key == key
    )

    coordinator = _create_coordinator(device)

    entity = VartaNumber(
        coordinator,
        _create_entry(),
        description,
    )

    return entity, coordinator, device


def test_maximum_discharging_power_value():
    """Test discharge limit value."""

    entity, _, _ = _create_number(
        "maximum_discharging_power"
    )

    assert entity.native_value == -5000.0


def test_maximum_charging_power_value():
    """Test charge limit value."""

    entity, _, _ = _create_number(
        "maximum_charging_power"
    )

    assert entity.native_value == 4500.0


def test_unique_id():
    """Test unique ID generation."""

    entity, _, _ = _create_number(
        "maximum_charging_power"
    )

    assert entity.unique_id == (
        "VARTA123_maximum_charging_power"
    )


def test_device_info():
    """Test device information."""

    entity, _, _ = _create_number(
        "maximum_charging_power"
    )

    assert entity.device_info["manufacturer"] == "VARTA"
    assert entity.device_info["serial_number"] == "VARTA123"


def test_number_limits():
    """Test configured limits."""

    discharge = next(
        item
        for item in NUMBERS
        if item.key == "maximum_discharging_power"
    )

    charge = next(
        item
        for item in NUMBERS
        if item.key == "maximum_charging_power"
    )

    assert discharge.native_min_value == -32768
    assert discharge.native_max_value == 0

    assert charge.native_min_value == 0
    assert charge.native_max_value == 32767


async def test_set_maximum_charging_power():
    """Test writing charging power."""

    entity, coordinator, device = _create_number(
        "maximum_charging_power"
    )

    await entity.async_set_native_value(6000)

    device.battery.write.assert_awaited_once_with(
        "maximum_charging_power",
        6000,
    )

    coordinator.async_request_refresh.assert_awaited_once()


async def test_set_maximum_discharging_power():
    """Test writing discharge power."""

    entity, coordinator, device = _create_number(
        "maximum_discharging_power"
    )

    await entity.async_set_native_value(-7000)

    device.battery.write.assert_awaited_once_with(
        "maximum_discharging_power",
        -7000,
    )

    coordinator.async_request_refresh.assert_awaited_once()
