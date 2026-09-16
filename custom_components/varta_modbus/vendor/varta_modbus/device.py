"""Top-level VARTA storage device."""

from modbus_connection import ModbusUnit
from modbus_connection.model import Device, UpdateReport

from .model import Battery, Grid, Identity


class VartaStorage(Device):
    """A VARTA storage system addressed as one Modbus unit."""

    def __init__(self, unit: ModbusUnit) -> None:
        super().__init__(unit)
        # Requirements are carried by the unit so callers retain connection ownership.
        unit.set_message_spacing(0.250)
        unit.require_timeout(3.0)
        unit.require_connect_delay(1.0)

        self.identity = Identity(unit)
        self.battery = Battery(unit)
        self.grid = Grid(unit)

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
            raise ValueError("device answered but did not expose a VARTA identity")
