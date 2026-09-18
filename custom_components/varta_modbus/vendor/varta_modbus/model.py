"""Register models for VARTA storage systems."""

from __future__ import annotations

from enum import IntEnum

from modbus_connection.model import (
    Component,
    enum,
    gauge,
    integer,
    string,
    uint32,
)


def validate_maximum_discharging_power(value: int) -> int:
    """Validate maximum discharge power."""
    value = int(value)

    if value != 0 and value > -500:
        raise ValueError(
            "Maximum discharge power must be 0 W or below -500 W"
        )

    return value


def validate_maximum_charging_power(value: int) -> int:
    """Validate maximum charge power."""
    value = int(value)

    if value != 0 and value < 500:
        raise ValueError(
            "Maximum charge power must be 0 W or above 500 W"
        )

    return value


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
    """EMS software version."""

    ens_software = string(1017, 17)
    """ENS software version."""

    software = string(1034, 17)
    """Main software version."""

    table_version = integer(1051, signed=False)
    """Register-table version."""

    serial_number = string(1054, 10)
    """Storage-system serial number."""

    installed_battery_modules = integer(
        1064,
        signed=False,
    )
    """Number of installed battery modules."""


class Battery(Component):
    """Battery operating measurements."""

    register_ranges = ((1065, 1075),)

    state = enum(
        1065,
        VartaState,
    )
    """Current operating state."""

    active_power = integer(
        1066,
        signed=True,
        unit="W",
    )
    """Battery active power; positive is charging, negative is discharging."""

    apparent_power = integer(
        1067,
        signed=True,
        unit="VA",
    )
    """Battery apparent power; positive is charging, negative is discharging."""

    state_of_charge = integer(
        1068,
        signed=False,
        unit="%",
    )
    """Battery state of charge."""

    ac_to_dc_energy = uint32(
        1069,
        word_order="little",
        unit="Wh",
    )
    """AC-to-DC energy counter."""

    installed_capacity = gauge(
        1071,
        10,
        signed=False,
        unit="Wh",
    )
    """Installed battery capacity."""
    error_code = gauge(
        1072,
        10,
        signed=False,
    )
    """Error Code"""
    
    external_control_timeout = integer(
        1073,
        signed=False,
        unit="s",
    )
    """Watchdog timer."""
    maximum_discharging_power = integer(
        1074,
        signed=True,
        unit="W",
        writable=validate_maximum_discharging_power,
    )
    """Maximum permitted discharge power."""

    maximum_charging_power = integer(
        1075,
        signed=True,
        unit="W",
        writable=validate_maximum_charging_power,
    )
    """Maximum permitted charge power."""

    @property
    def charging_power(self) -> int | None:
        """Charging power as a positive value."""
        if self.active_power is None:
            return None

        return max(self.active_power, 0)

    @property
    def discharging_power(self) -> int | None:
        """Discharging power as a positive value."""
        if self.active_power is None:
            return None

        return max(-self.active_power, 0)


class Grid(Component):
    """Grid-side measurements."""

    register_ranges = ((1078, 1078),)

    power = integer(
        1078,
        signed=True,
        unit="W",
    )
    """Signed grid power reported by the storage system."""
