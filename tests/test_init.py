"""Tests for VARTA Modbus integration setup."""

from unittest.mock import AsyncMock, MagicMock, patch

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.varta_modbus.const import DOMAIN


VALID_CONFIG = {
    "host": "192.168.1.100",
    "port": 502,
    "unit_id": 1,
}


async def test_setup_entry(hass):
    """Test config entry setup."""

    entry = MockConfigEntry(
        domain=DOMAIN,
        title="VARTA Modbus",
        data=VALID_CONFIG,
    )
    entry.add_to_hass(hass)

    mock_unit = MagicMock()
    mock_device = MagicMock()

    mock_coordinator = MagicMock()
    mock_coordinator.async_config_entry_first_refresh = AsyncMock()

    with (
        patch(
            "custom_components.varta_modbus.async_get_unit",
            return_value=mock_unit,
        ),
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

        assert await async_setup_entry(
            hass,
            entry,
        )

    mock_coordinator.async_config_entry_first_refresh.assert_awaited_once()

    mock_forward.assert_awaited_once()

    assert entry.runtime_data.device is mock_device
    assert entry.runtime_data.coordinator is mock_coordinator


async def test_unload_entry(hass):
    """Test unloading a config entry."""

    entry = MockConfigEntry(
        domain=DOMAIN,
        title="VARTA Modbus",
        data=VALID_CONFIG,
    )
    entry.add_to_hass(hass)

    with patch.object(
        hass.config_entries,
        "async_unload_platforms",
        AsyncMock(return_value=True),
    ) as mock_unload:
        from custom_components.varta_modbus import async_unload_entry

        result = await async_unload_entry(
            hass,
            entry,
        )

    assert result is True

    mock_unload.assert_awaited_once()


async def test_runtime_data_created(hass):
    """Verify runtime data assignment."""

    entry = MockConfigEntry(
        domain=DOMAIN,
        title="VARTA Modbus",
        data=VALID_CONFIG,
    )
    entry.add_to_hass(hass)

    mock_unit = MagicMock()
    mock_device = MagicMock()

    mock_coordinator = MagicMock()
    mock_coordinator.async_config_entry_first_refresh = AsyncMock()

    with (
        patch(
            "custom_components.varta_modbus.async_get_unit",
            return_value=mock_unit,
        ),
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
            AsyncMock
