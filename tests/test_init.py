"""Tests for VARTA Modbus integration setup and unload."""

from unittest.mock import AsyncMock, MagicMock, patch

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.varta_modbus.const import DOMAIN


VALID_CONFIG = {
    "host": "192.168.1.100",
    "port": 502,
    "unit_id": 1,
}


def _create_entry():
    """Create a test config entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="VARTA Modbus",
        data=VALID_CONFIG,
    )
    return entry


def _create_device():
    """Create a fake VARTA device."""
    device = MagicMock()
    device.external_control.async_stop = AsyncMock()
    return device


def _create_coordinator():
    """Create a fake VARTA coordinator."""
    coordinator = MagicMock()
    coordinator.async_config_entry_first_refresh = AsyncMock()
    return coordinator


async def test_setup_entry(hass):
    """Test config entry setup."""
    entry = _create_entry()
    entry.add_to_hass(hass)

    mock_unit = MagicMock()
    mock_device = _create_device()
    mock_coordinator = _create_coordinator()

    with (
        patch(
            "custom_components.varta_modbus.async_get_unit",
            return_value=mock_unit,
        ) as mock_get_unit,
        patch(
            "custom_components.varta_modbus.VartaStorage",
            return_value=mock_device,
        ),
        patch(
            "custom_components.varta_modbus.VartaCoordinator",
            return_value=mock_coordinator,
        ),
        patch.object(
            hass.config_entries,
            "async_forward_entry_setups",
            AsyncMock(),
        ) as mock_forward,
    ):
        from custom_components.varta_modbus import async_setup_entry

        result = await async_setup_entry(hass, entry)

    assert result is True

    mock_get_unit.assert_called_once()
    mock_coordinator.async_config_entry_first_refresh.assert_awaited_once()
    mock_forward.assert_awaited_once()

    assert entry.runtime_data.device is mock_device
    assert entry.runtime_data.coordinator is mock_coordinator


async def test_unload_entry(hass):
    """Test unloading a config entry."""
    entry = _create_entry()
    entry.add_to_hass(hass)

    mock_device = _create_device()
    entry.runtime_data = MagicMock(
        device=mock_device,
        coordinator=MagicMock(),
    )

    with patch.object(
        hass.config_entries,
        "async_unload_platforms",
        AsyncMock(return_value=True),
    ) as mock_unload:
        from custom_components.varta_modbus import async_unload_entry

        result = await async_unload_entry(hass, entry)

    assert result is True
    mock_unload.assert_awaited_once()
    mock_device.external_control.async_stop.assert_awaited_once()


async def test_unload_entry_keeps_watchdog_running_when_platform_unload_fails(
    hass,
):
    """Test watchdog is not stopped when platform unload fails."""
    entry = _create_entry()
    entry.add_to_hass(hass)

    mock_device = _create_device()
    entry.runtime_data = MagicMock(
        device=mock_device,
        coordinator=MagicMock(),
    )

    with patch.object(
        hass.config_entries,
        "async_unload_platforms",
        AsyncMock(return_value=False),
    ) as mock_unload:
        from custom_components.varta_modbus import async_unload_entry

        result = await async_unload_entry(hass, entry)

    assert result is False
    mock_unload.assert_awaited_once()
    mock_device.external_control.async_stop.assert_not_awaited()
