"""Tests for the VARTA storage device wrapper."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.varta_modbus.vendor.varta_modbus.device import (
    VARTA_MESSAGE_SPACING,
    VartaStorage,
)


def _create_unit(*, has_spacing: bool = True) -> MagicMock:
    """Create a mock ModbusUnit."""
    unit = MagicMock()
    if has_spacing:
        unit.set_message_spacing = MagicMock()
    else:
        del unit.set_message_spacing
    return unit


def test_storage_init_sets_message_spacing() -> None:
    """Test initialization configures message spacing when supported."""
    unit = _create_unit(has_spacing=True)

    storage = VartaStorage(unit)

    unit.set_message_spacing.assert_called_once_with(VARTA_MESSAGE_SPACING)
    assert storage.identity is not None
    assert storage.battery is not None
    assert storage.grid is not None
    assert storage.external_control is not None


def test_storage_init_without_message_spacing(caplog) -> None:
    """Test initialization logs warning if unit lacks set_message_spacing."""
    unit = _create_unit(has_spacing=False)

    with caplog.at_level("WARNING"):
        storage = VartaStorage(unit)

    assert "does not support per-unit message spacing" in caplog.text
    assert storage.identity is not None


async def test_storage_async_setup() -> None:
    """Test _async_setup reads initial identity data."""
    unit = _create_unit()
    storage = VartaStorage(unit)
    storage.identity.async_update = AsyncMock()

    await storage._async_setup()

    storage.identity.async_update.assert_awaited_once()


async def test_storage_update_methods() -> None:
    """Test async_update_readings, async_update_identity, and async_update."""
    unit = _create_unit()
    storage = VartaStorage(unit)

    mock_report = SimpleNamespace(ok=True)
    with patch.object(
        storage,
        "async_poll",
        AsyncMock(return_value=mock_report),
    ) as mock_poll:
        res_readings = await storage.async_update_readings()
        assert res_readings is mock_report
        mock_poll.assert_awaited_with(("battery", "grid"))

        res_identity = await storage.async_update_identity()
        assert res_identity is mock_report
        mock_poll.assert_awaited_with(("identity",))

        mock_poll.reset_mock()
        res_all = await storage.async_update()
        assert res_all is mock_report
        assert mock_poll.await_count == 2
        mock_poll.assert_any_await(("battery", "grid"))
        mock_poll.assert_any_await(("identity",), report=mock_report)


async def test_storage_async_validate_success() -> None:
    """Test async_validate succeeds when identity data is exposed."""
    unit = _create_unit()
    storage = VartaStorage(unit)

    async def fake_ensure_setup() -> None:
        storage.identity.serial_number = "12345678"
        storage.identity.table_version = None

    with patch.object(
        storage,
        "async_ensure_setup",
        side_effect=fake_ensure_setup,
    ) as mock_ensure:
        await storage.async_validate()

    mock_ensure.assert_awaited_once()


async def test_storage_async_validate_raises_on_empty_identity() -> None:
    """Test async_validate raises ValueError when identity fields are empty."""
    unit = _create_unit()
    storage = VartaStorage(unit)
    storage.identity.serial_number = None
    storage.identity.table_version = None

    with (
        patch.object(
            storage,
            "async_ensure_setup",
            AsyncMock(),
        ),
        pytest.raises(
            ValueError,
            match="Device answered but did not expose a VARTA identity",
        ),
    ):
        await storage.async_validate()
