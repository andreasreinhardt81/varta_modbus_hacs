"""Top-level VARTA storage device."""

from __future__ import annotations

import logging

from modbus_connection import ModbusUnit
from modbus_connection.model import Device, UpdateReport

from .model import Battery, Grid, Identity
from .external_control import ExternalControl

_LOGGER = logging.getLogger(__name__)

VARTA_MESSAGE_SPACING = 1.5
VARTA_TIMEOUT = 3.0
VARTA_CONNECT_DELAY = 1.0

class VartaStorage(Device):
    """A VARTA storage system addressed as one Modbus unit."""

    def __init__(self, unit: ModbusUnit) -> None:
        """Initialize the VARTA storage device."""
        super().__init__(unit)
        
        # VARTA devices need conservative communication timing.
        #
        # These methods are part of the current modbus-connection API.
        # The getattr checks keep the library compatible with older
        # modbus-connection versions that may still be present in HA.
        set_message_spacing = getattr(unit, "set_message_spacing", None)
        if set_message_spacing is not None:
            set_message_spacing(VARTA_MESSAGE_SPACING)
        else:
            _LOGGER.warning(
                "The installed modbus-connection version does not support "
                "per-unit message spacing. VARTA requires approximately "
                "%s seconds between requests.",
                VARTA_MESSAGE_SPACING,
            )

        require_timeout = getattr(unit, "require_timeout", None)
        if require_timeout is not None:
            require_timeout(VARTA_TIMEOUT)
        else:
            _LOGGER.warning(
                "The installed modbus-connection version does not support "
                "per-unit timeout requirements. VARTA normally requires "
                "a %s second timeout.",
                VARTA_TIMEOUT,
            )

        require_connect_delay = getattr(unit, "require_connect_delay", None)
        if require_connect_delay is not None:
            require_connect_delay(VARTA_CONNECT_DELAY)
        else:
            _LOGGER.warning(
                "The installed modbus-connection version does not support "
                "per-unit connect delay requirements. VARTA normally requires "
                "a %s second connect delay.",
                VARTA_CONNECT_DELAY,
            )

        self.identity = Identity(unit)
        self.battery = Battery(unit)
        self.grid = Grid(unit)
        self.external_control = ExternalControl(self.battery)
        
    async def _async_setup(self) -> None:
        """Read stable identity data before normal polling."""
        await self.identity.async_update()

    async def async_update_readings(self) -> UpdateReport:
        """Refresh changing measurements."""
        return await self.async_poll(("battery", "grid"))

    async def async_update_identity(self) -> UpdateReport:
        """Refresh identity and software information."""
        return await self.async_poll(("identity",))

    async def async_update(self) -> UpdateReport:
        """Refresh all exposed components."""
        report = await self.async_poll(("battery", "grid"))
        return await self.async_poll(("identity",), report=report)

    async def async_validate(self) -> None:
        """Verify that the target answers with VARTA-shaped identity data."""
        await self.async_ensure_setup()

        if not self.identity.serial_number and not self.identity.table_version:
            raise ValueError(
                "Device answered but did not expose a VARTA identity"
            )
