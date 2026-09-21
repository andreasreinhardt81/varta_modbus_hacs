"""Tests for VARTA Modbus number entities."""

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from custom_components.varta_modbus.number import (
    NUMBERS,
    VartaNumber,
)


def _create_device():
    """Create test device."""
    battery = SimpleNamespace(
        maximum_discharging_power=-4000,
        maximum_charging_power=3500,
    )

    external_control = SimpleNamespace(
        async_set_discharging_power=AsyncMock(),
        async_set_charging_power=AsyncMock(),
    )

    return SimpleNamespace(
        identity=SimpleNamespace(
            serial_number="VARTA123",
            software="1.0.0",
        ),
        battery=battery,
        external_control=external_control,
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

    assert entity.native_value == -4000.0


def test_maximum_charging_power_value():
    """Test charge limit value."""
    entity, _, _ = _create_number(
        "maximum_charging_power"
    )

    assert entity.native_value == 3500.0


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
    """Test configured number limits."""
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

    assert discharge.native_min_value == -4000
    assert discharge.native_max_value == 0
    assert discharge.native_step == 1

    assert charge.native_min_value == 0
    assert charge.native_max_value == 4000
    assert charge.native_step == 1


async def test_set_maximum_charging_power():
    """Test writing charging power through external control."""
    entity, coordinator, device = _create_number(
        "maximum_charging_power"
    )

    await entity.async_set_native_value(3000)

    device.external_control.async_set_charging_power.assert_awaited_once_with(
        3000
    )
    device.external_control.async_set_discharging_power.assert_not_awaited()

    coordinator.async_request_refresh.assert_awaited_once()


async def test_set_maximum_discharging_power():
    """Test writing discharge power through external control."""
    entity, coordinator, device = _create_number(
        "maximum_discharging_power"
    )

    await entity.async_set_native_value(-2000)

    device.external_control.async_set_discharging_power.assert_awaited_once_with(
        -2000
    )
    device.external_control.async_set_charging_power.assert_not_awaited()

    coordinator.async_request_refresh.assert_awaited_once()


@pytest.mark.parametrize(
    "value",
    [-500, -1000, -4000],
)
async def test_set_valid_maximum_discharging_power(
    value: int,
):
    """Test valid discharge power values."""
    entity, coordinator, device = _create_number(
        "maximum_discharging_power"
    )

    await entity.async_set_native_value(value)

    device.external_control.async_set_discharging_power.assert_awaited_once_with(
        value
    )
    coordinator.async_request_refresh.assert_awaited_once()


@pytest.mark.parametrize(
    "value",
    [0],
)
async def test_set_zero_maximum_discharging_power(
    value: int,
):
    """Test zero discharge power."""
    entity, coordinator, device = _create_number(
        "maximum_discharging_power"
    )

    await entity.async_set_native_value(value)

    device.external_control.async_set_discharging_power.assert_awaited_once_with(
        value
    )
    coordinator.async_request_refresh.assert_awaited_once()


@pytest.mark.parametrize(
    "value",
    [-499, -498, -1],
)
async def test_reject_invalid_maximum_discharging_power(
    value: int,
):
    """Test invalid discharge power values are rejected."""
    entity, coordinator, device = _create_number(
        "maximum_discharging_power"
    )

    with pytest.raises(ValueError):
        await entity.async_set_native_value(value)

    device.external_control.async_set_discharging_power.assert_not_awaited()
    coordinator.async_request_refresh.assert_not_awaited()


@pytest.mark.parametrize(
    "value",
    [500, 1000, 4000],
)
async def test_set_valid_maximum_charging_power(
    value: int,
):
    """Test valid charge power values."""
    entity, coordinator, device = _create_number(
        "maximum_charging_power"
    )

    await entity.async_set_native_value(value)

    device.external_control.async_set_charging_power.assert_awaited_once_with(
        value
    )
    coordinator.async_request_refresh.assert_awaited_once()


@pytest.mark.parametrize(
    "value",
    [0],
)
async def test_set_zero_maximum_charging_power(
    value: int,
):
    """Test zero charge power."""
    entity, coordinator, device = _create_number(
        "maximum_charging_power"
    )

    await entity.async_set_native_value(value)

    device.external_control.async_set_charging_power.assert_awaited_once_with(
        value
    )
    coordinator.async_request_refresh.assert_awaited_once()


@pytest.mark.parametrize(
    "value",
    [1, 498, 499],
)
async def test_reject_invalid_maximum_charging_power(
    value: int,
):
    """Test invalid charge power values are rejected."""
    entity, coordinator, device = _create_number(
        "maximum_charging_power"
    )

    with pytest.raises(ValueError):
        await entity.async_set_native_value(value)

    device.external_control.async_set_charging_power.assert_not_awaited()
    coordinator.async_request_refresh.assert_not_awaited()
