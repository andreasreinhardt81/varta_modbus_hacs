"""Tests for the VARTA Modbus config flow."""

from unittest.mock import AsyncMock, patch

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT

from custom_components.varta_modbus.const import (
    CONF_UNIT_ID,
    DOMAIN,
)

VALID_INPUT = {
    CONF_HOST: "192.168.178.100",
    CONF_PORT: 502,
    CONF_UNIT_ID: 1,
}


async def test_create_entry_success(hass):
    """Test successful config flow."""

    with patch(
        "custom_components.varta_modbus.config_flow.async_validate_input",
        AsyncMock(),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_USER},
        )

        assert result["type"] == "form"

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            VALID_INPUT,
        )

    assert result["type"] == "create_entry"
    assert result["title"] == "VARTA Modbus"
    assert result["data"] == VALID_INPUT


async def test_create_entry_connection_error(hass):
    """Test failed connection check."""

    with patch(
        "custom_components.varta_modbus.config_flow.async_validate_input",
        side_effect=ValueError,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_USER},
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            VALID_INPUT,
        )

    assert result["type"] == "form"
    assert result["errors"]["base"] == "cannot_connect"


async def test_reconfigure_success(hass):
    """Test successful reconfiguration."""

    entry = hass.config_entries.async_entries(DOMAIN)

    if not entry:
        entry = hass.config_entries.async_add(
            config_entries.ConfigEntry(
                version=1,
                minor_version=1,
                domain=DOMAIN,
                title="VARTA Modbus",
                data=VALID_INPUT,
                source="user",
                entry_id="test",
                discovery_keys={},
                options={},
            )
        )

    with patch(
        "custom_components.varta_modbus.config_flow.async_validate_input",
        AsyncMock(),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={
                "source": config_entries.SOURCE_RECONFIGURE,
                "entry_id": entry.entry_id,
            },
            data=entry.data,
        )

        assert result["type"] == "form"

        new_data = {
            CONF_HOST: "192.168.178.101",
            CONF_PORT: 502,
            CONF_UNIT_ID: 2,
        }

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input=new_data,
        )

    assert result["type"] == "abort"
    assert result["reason"] == "reconfigure_successful"


async def test_reconfigure_failed_validation(hass):
    """Test failed reconfiguration."""

    entry = hass.config_entries.async_entries(DOMAIN)

    if not entry:
        return

    entry = entry[0]

    with patch(
        "custom_components.varta_modbus.config_flow.async_validate_input",
        side_effect=ValueError,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={
                "source": config_entries.SOURCE_RECONFIGURE,
                "entry_id": entry.entry_id,
            },
            data=entry.data,
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            VALID_INPUT,
        )

    assert result["type"] == "form"
    assert result["errors"]["base"] == "cannot_connect"
