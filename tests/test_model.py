"""Tests for VARTA Modbus register models."""

from unittest.mock import MagicMock

import pytest

from custom_components.varta_modbus.vendor.varta_modbus.model import (
    Battery,
    validate_maximum_charging_power,
    validate_maximum_discharging_power,
)


@pytest.mark.parametrize("value", [-499, -1])
def test_validate_maximum_discharging_power_rejects_invalid(value: int) -> None:
    """Test invalid discharge limits raise ValueError."""
    with pytest.raises(ValueError, match="below -500 W"):
        validate_maximum_discharging_power(value)


@pytest.mark.parametrize("value", [1, 499])
def test_validate_maximum_charging_power_rejects_invalid(value: int) -> None:
    """Test invalid charge limits raise ValueError."""
    with pytest.raises(ValueError, match="above 500 W"):
        validate_maximum_charging_power(value)


def test_battery_charging_and_discharging_power() -> None:
    """Test derived charging_power and discharging_power properties."""
    battery = Battery(MagicMock())

    # 1. None when active_power has not been read yet
    battery.active_power = None
    assert battery.charging_power is None
    assert battery.discharging_power is None

    # 2. Charging (positive active_power)
    battery.active_power = 1200
    assert battery.charging_power == 1200
    assert battery.discharging_power == 0

    # 3. Discharging (negative active_power)
    battery.active_power = -850
    assert battery.charging_power == 0
    assert battery.discharging_power == 850
