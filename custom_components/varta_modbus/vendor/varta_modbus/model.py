"""Register models for VARTA storage systems."""

from enum import IntEnum

from modbus_connection.model import Component, enum, gauge, integer, string, uint32


class VartaState(IntEnum):
    """Operating state reported by register 1065."""

    BUSY = 0
    RUN = 1
    CHARGE = 2
    DISCHARGE = 3
    STANDBY = 4
    ERROR = 5
    SERVICE = 6
    ISLANDING = 7


class Identity(Component):
    """Identity and software information."""

    register_ranges = ((1000, 1064),)

    ems_software = string(1000, 17)
    """EMS software version (not available on every model)."""

    ens_software = string(1017, 17)
    """ENS software version (not available on every model)."""

    software = string(1034, 17)
    """Main software version (not available on every model)."""

    table_version = integer(1051, signed=False)
    """Register-table version."""

    timestamp = uint32(1052, word_order="little")
    """Device timestamp; some firmware is known to return an unusable value."""

    serial_number = string(1054, 10)
    """Storage-system serial number."""

    installed_battery_modules = integer(1064, signed=False)
    """Number of installed battery modules."""


class Battery(Component):
    """Battery operating measurements."""

    register_ranges = ((1065, 1075),)

    state = enum(1065, VartaState)
    """Current operating state."""

    active_power = integer(1066, signed=True, unit="W")
    """Battery active power; positive is charging, negative is discharging."""

    apparent_power = integer(1067, signed=True, unit="VA")
    """Battery apparent power; positive is charging, negative is discharging."""

    state_of_charge = integer(1068, signed=False, unit="%")
    """Battery state of charge."""

    ac_to_dc_energy = uint32(1069, word_order="little", unit="Wh")
    """AC-to-DC energy counter."""

    installed_capacity = gauge(1071, 10, signed=False, unit="Wh")
    """Installed battery capacity."""

    maximum_discharging_power = integer(1074, signed=True, unit="W", writable=True)
    """Maximum permitted discharge power; VARTA uses negative values (for example -4000 W)."""

    maximum_charging_power = integer(1075, signed=True, unit="W", writable=True)
    """Maximum permitted charge power; VARTA uses positive values (for example 4000 W)."""

    @property
    def charging_power(self) -> int | None:
        """Charging power as a positive value."""
        return None if self.active_power is None else max(self.active_power, 0)

    @property
    def discharging_power(self) -> int | None:
        """Discharging power as a positive value."""
        return None if self.active_power is None else max(-self.active_power, 0)


class Grid(Component):
    """Grid-side measurements."""

    register_ranges = ((1078, 1078),)

    power = integer(1078, signed=True, unit="W")
    """Signed grid power reported by the storage system."""
