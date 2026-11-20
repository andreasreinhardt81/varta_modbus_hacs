"""Tests for the VARTA Modbus data update coordinator."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.helpers.update_coordinator import UpdateFailed
from modbus_connection import ModbusError

from custom_components.varta_modbus.coordinator import VartaCoordinator


async def test_coordinator_update_success(hass) -> None:
    """Test successful coordinator data update."""
    device = MagicMock()
    device.async_update_readings = AsyncMock()

    coordinator = VartaCoordinator(hass, device)
    assert coordinator.device is device

    await coordinator._async_update_data()

    device.async_update_readings.assert_awaited_once()


async def test_coordinator_update_modbus_error(hass) -> None:
    """Test coordinator raises UpdateFailed on ModbusError."""
    device = MagicMock()
    device.async_update_readings = AsyncMock(
        side_effect=ModbusError("connection lost")
    )

    coordinator = VartaCoordinator(hass, device)

    with pytest.raises(UpdateFailed, match="connection lost"):
        await coordinator._async_update_data()
