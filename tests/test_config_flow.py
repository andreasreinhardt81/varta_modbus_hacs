"""Tests for the VARTA Modbus config flow."""

from unittest.mock import AsyncMock, patch

from homeassistant.config_entries import SOURCE_RECONFIGURE, SOURCE_USER
from homeassistant.data_entry_flow import FlowResultType

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.varta_modbus.const import (
    CONF_UNIT_ID,
    DEFAULT_PORT,
    DOMAIN,
)

VALID_INPUT = {
    "host": "192.168.1.100",
    "port": DEFAULT_PORT,
    CONF_UNIT_ID: 1,
}


async def test_user_flow_create_entry(hass):
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

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            VALID_INPUT,
        )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "VARTA Modbus"
    assert result["data"] == VALID_INPUT


async def test_user_flow_connection_error(hass):
    """Test validation failure."""

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


async def test_reconfigure_success(hass):
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
            data=entry.data,
        )

        assert result["type"] == FlowResultType.FORM

        new_data = {
            "host": "192.168.1.101",
            "port": DEFAULT_PORT,
            CONF_UNIT_ID: 2,
        }

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            new_data,
        )

    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"


async def test_reconfigure_validation_error(hass):
    """Test failed reconfiguration."""

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
            data=entry.data,
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            VALID_INPUT,
        )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"]["base"] == "cannot_connect"
