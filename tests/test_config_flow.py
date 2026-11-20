"""Tests for the VARTA Modbus config flow."""

from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.config_entries import SOURCE_RECONFIGURE, SOURCE_USER
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.varta_modbus.config_flow import async_validate_input
from custom_components.varta_modbus.const import (
    CONF_UNIT_ID,
    DEFAULT_PORT,
    DOMAIN,
)

VALID_INPUT = {
    CONF_HOST: "192.168.1.100",
    CONF_PORT: DEFAULT_PORT,
    CONF_UNIT_ID: 1,
}


@pytest.fixture(autouse=True)
def mock_setup_entry() -> Generator[AsyncMock]:
    """Prevent actual integration setup during config flow tests."""
    with patch(
        "custom_components.varta_modbus.async_setup_entry",
        return_value=True,
    ) as mock_setup:
        yield mock_setup


async def test_async_validate_input(hass) -> None:
    """Test async_validate_input creates temporary unit and validates storage."""
    mock_unit = MagicMock()
    mock_cm = MagicMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_unit)
    mock_cm.__aexit__ = AsyncMock(return_value=None)

    mock_device = MagicMock()
    mock_device.async_validate = AsyncMock()

    with (
        patch(
            "custom_components.varta_modbus.config_flow.async_get_temporary_unit",
            return_value=mock_cm,
        ) as mock_get_unit,
        patch(
            "custom_components.varta_modbus.config_flow.VartaStorage",
            return_value=mock_device,
        ) as mock_storage_cls,
    ):
        await async_validate_input(
            hass,
            {
                CONF_HOST: " 192.168.1.100 ",
                CONF_PORT: DEFAULT_PORT,
                CONF_UNIT_ID: 1,
            },
        )

    mock_get_unit.assert_called_once()
    call_args = mock_get_unit.call_args.args
    assert call_args[0] is hass
    assert call_args[1].host == "192.168.1.100"
    assert call_args[1].port == DEFAULT_PORT
    assert call_args[2] == 1

    mock_storage_cls.assert_called_once_with(mock_unit)
    mock_device.async_validate.assert_awaited_once()


async def test_user_flow_create_entry(hass) -> None:
    """Test successful user setup."""
    with patch(
        "custom_components.varta_modbus.config_flow.async_validate_input",
        AsyncMock(),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": SOURCE_USER},
        )

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "user"

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            VALID_INPUT,
        )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "VARTA Modbus"
    assert result["data"] == VALID_INPUT


async def test_user_flow_strips_whitespace(hass) -> None:
    """Test leading and trailing whitespace in host is stripped."""
    with patch(
        "custom_components.varta_modbus.config_flow.async_validate_input",
        AsyncMock(),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": SOURCE_USER},
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_HOST: "  192.168.1.100  ",
                CONF_PORT: DEFAULT_PORT,
                CONF_UNIT_ID: 1,
            },
        )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["data"] == VALID_INPUT


async def test_user_flow_connection_error(hass) -> None:
    """Test validation failure shows cannot_connect error."""
    with patch(
        "custom_components.varta_modbus.config_flow.async_validate_input",
        side_effect=ValueError,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": SOURCE_USER},
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            VALID_INPUT,
        )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"]["base"] == "cannot_connect"


async def test_user_flow_already_configured(hass) -> None:
    """Test duplicate entry aborts with already_configured."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="VARTA Modbus",
        data=VALID_INPUT,
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_USER},
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        VALID_INPUT,
    )

    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_reconfigure_success(hass) -> None:
    """Test successful reconfiguration."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="VARTA Modbus",
        data=VALID_INPUT,
    )
    entry.add_to_hass(hass)

    with patch(
        "custom_components.varta_modbus.config_flow.async_validate_input",
        AsyncMock(),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={
                "source": SOURCE_RECONFIGURE,
                "entry_id": entry.entry_id,
            },
        )

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "reconfigure"

        new_data = {
            CONF_HOST: "192.168.1.101",
            CONF_PORT: DEFAULT_PORT,
            CONF_UNIT_ID: 2,
        }

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            new_data,
        )

    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert entry.data == new_data


async def test_reconfigure_validation_error(hass) -> None:
    """Test failed reconfiguration shows cannot_connect error."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="VARTA Modbus",
        data=VALID_INPUT,
    )
    entry.add_to_hass(hass)

    with patch(
        "custom_components.varta_modbus.config_flow.async_validate_input",
        side_effect=ValueError,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={
                "source": SOURCE_RECONFIGURE,
                "entry_id": entry.entry_id,
            },
        )

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "reconfigure"

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            VALID_INPUT,
        )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"]["base"] == "cannot_connect"
