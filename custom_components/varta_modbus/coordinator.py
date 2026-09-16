"""Data update coordinator for VARTA Modbus."""

from datetime import timedelta
import logging

from modbus_connection import ModbusError

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .vendor.varta_modbus import VartaStorage

_LOGGER = logging.getLogger(__name__)


class VartaCoordinator(DataUpdateCoordinator[None]):
    """Poll the changing VARTA measurements."""

    def __init__(self, hass: HomeAssistant, device: VartaStorage) -> None:
        super().__init__(
            hass,
            logger=_LOGGER,
            name="VARTA Modbus",
            update_interval=timedelta(seconds=30),
        )
        self.device = device

    async def _async_update_data(self) -> None:
        try:
            await self.device.async_update_readings()
        except ModbusError as err:
            raise UpdateFailed(str(err)) from err
