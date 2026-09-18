"""Sensor platform for VARTA Modbus."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, override

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    EntityCategory,
    UnitOfApparentPower,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import VartaConfigEntry
from .const import DOMAIN
from .coordinator import VartaCoordinator
from .vendor.varta_modbus import VartaStorage


@dataclass(frozen=True, kw_only=True)
class VartaSensorDescription(SensorEntityDescription):
    """Describe a VARTA sensor."""

    value_fn: Callable[[VartaStorage], Any]


SENSORS = (
    VartaSensorDescription(
        key="state",
        translation_key="state",
        device_class=SensorDeviceClass.ENUM,
        options=[
            "busy",
            "run",
            "charge",
            "discharge",
            "standby",
            "error",
            "service",
            "islanding",
        ],
        value_fn=lambda device: (
            device.battery.state.name.lower()
            if device.battery.state is not None
            else None
        ),
    ),
    VartaSensorDescription(
        key="active_power",
        translation_key="active_power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.battery.active_power,
    ),
    VartaSensorDescription(
        key="charging_power",
        translation_key="charging_power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.battery.charging_power,
    ),
    VartaSensorDescription(
        key="discharging_power",
        translation_key="discharging_power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.battery.discharging_power,
    ),
    VartaSensorDescription(
        key="apparent_power",
        translation_key="apparent_power",
        device_class=SensorDeviceClass.APPARENT_POWER,
        native_unit_of_measurement=UnitOfApparentPower.VOLT_AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.battery.apparent_power,
    ),
    VartaSensorDescription(
        key="state_of_charge",
        translation_key="state_of_charge",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.battery.state_of_charge,
    ),
    VartaSensorDescription(
        key="ac_to_dc_energy",
        translation_key="ac_to_dc_energy",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda device: device.battery.ac_to_dc_energy,
    ),
    VartaSensorDescription(
        key="installed_capacity",
        translation_key="installed_capacity",
        device_class=SensorDeviceClass.ENERGY_STORAGE,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        value_fn=lambda device: device.battery.installed_capacity,
    ),
    VartaSensorDescription(
        key="error_code",
        translation_key="error_code",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda device: device.battery.error_code,
    ),
    VartaSensorDescription(
        key="grid_power",
        translation_key="grid_power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.grid.power,
    ),
    VartaSensorDescription(
        key="external_control_timeout",
        translation_key="external_control_timeout",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda device: device.battery.external_control_timeout,
    ),
    VartaSensorDescription(
        key="installed_battery_modules",
        translation_key="installed_battery_modules",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda device: device.identity.installed_battery_modules,
    ),
    VartaSensorDescription(
        key="table_version",
        translation_key="table_version",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda device: device.identity.table_version,
    ),
    VartaSensorDescription(
        key="ems_software",
        translation_key="ems_software",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda device: device.identity.ems_software,
    ),
    VartaSensorDescription(
        key="ens_software",
        translation_key="ens_software",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda device: device.identity.ens_software,
    ),
    VartaSensorDescription(
        key="software",
        translation_key="software",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda device: device.identity.software,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: VartaConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up VARTA sensors."""
    async_add_entities(
        VartaSensor(
            entry.runtime_data.coordinator,
            entry,
            description,
        )
        for description in SENSORS
    )


class VartaSensor(
    CoordinatorEntity[VartaCoordinator],
    SensorEntity,
):
    """A VARTA Modbus sensor."""

    entity_description: VartaSensorDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: VartaCoordinator,
        entry: VartaConfigEntry,
        description: VartaSensorDescription,
    ) -> None:
        """Initialize the sensor."""
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
    def native_value(self) -> Any:
        """Return the sensor value."""
        return self.entity_description.value_fn(
            self.coordinator.device
        )
