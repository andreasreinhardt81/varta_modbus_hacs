"""Number platform for writable VARTA Modbus limits."""

from __future__ import annotations

from dataclasses import dataclass
from typing import override

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
)
from homeassistant.const import EntityCategory, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import VartaConfigEntry
from .const import DOMAIN
from .coordinator import VartaCoordinator


@dataclass(frozen=True, kw_only=True)
class VartaNumberDescription(NumberEntityDescription):
    """Describe a writable VARTA number."""

    field: str


NUMBERS = (
    VartaNumberDescription(
        key="maximum_discharging_power",
        translation_key="maximum_discharging_power",
        field="maximum_discharging_power",
        native_unit_of_measurement=UnitOfPower.WATT,
        native_min_value=-32768,
        native_max_value=0,
        native_step=1,
        entity_category=EntityCategory.CONFIG,
    ),
    VartaNumberDescription(
        key="maximum_charging_power",
        translation_key="maximum_charging_power",
        field="maximum_charging_power",
        native_unit_of_measurement=UnitOfPower.WATT,
        native_min_value=0,
        native_max_value=32767,
        native_step=1,
        entity_category=EntityCategory.CONFIG,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: VartaConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up VARTA writable numbers."""
    async_add_entities(
        VartaNumber(
            entry.runtime_data.coordinator,
            entry,
            description,
        )
        for description in NUMBERS
    )


class VartaNumber(
    CoordinatorEntity[VartaCoordinator],
    NumberEntity,
):
    """A writable VARTA Modbus number."""

    entity_description: VartaNumberDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: VartaCoordinator,
        entry: VartaConfigEntry,
        description: VartaNumberDescription,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)

        self.entity_description = description

        device = coordinator.device
        serial = device.identity.serial_number or entry.entry_id

        self._attr_unique_id = f"{serial}_{description.key}"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, serial)},
            manufacturer="VARTA",
            name="VARTA Modbus",
            serial_number=device.identity.serial_number,
            sw_version=device.identity.software,
        )

    @property
    @override
    def native_value(self) -> float | None:
        """Return the current VARTA power limit."""
        value = getattr(
            self.coordinator.device.battery,
            self.entity_description.field,
        )

        return float(value) if value is not None else None

    async def async_set_native_value(
        self,
        value: float,
    ) -> None:
        """Write the requested VARTA power limit."""
        await self.coordinator.device.battery.write(
            self.entity_description.field,
            int(value),
        )

        await self.coordinator.async_request_refresh()
