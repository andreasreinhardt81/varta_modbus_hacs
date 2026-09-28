"""Vendored copy of modbus_connection.model.Device and UpdateReport.

Taken from home-assistant-libs/modbus-connection (main branch) because
these classes are not yet exported in the modbus-connection 4.12.1 release
that ships with Home Assistant 2026.9.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from modbus_connection.exceptions import (
    IllegalDataAddressError,
    IllegalFunctionError,
    ModbusConnectionError,
    ModbusError,
    ModbusTimeoutError,
)

if TYPE_CHECKING:
    from modbus_connection._protocol import ModbusUnit


@dataclass
class UpdateReport:
    """What one poll managed to refresh."""

    updated: set[str] = field(default_factory=set)
    failed: dict[str, ModbusError] = field(default_factory=dict)

    @property
    def complete(self) -> bool:
        """Whether every sub-system the poll covered refreshed."""
        return not self.failed


async def read_optional(component):
    """Read an optional sub-system; None if the device does not serve it."""
    try:
        await component.async_update()
    except (IllegalDataAddressError, IllegalFunctionError):
        return None
    return component


class Device:
    """Hold a device's components and poll them by attribute name."""

    def __init__(self, unit) -> None:
        self.modbus_unit = unit
        self._setup_done = False

    async def _async_setup(self) -> None:
        """Read what never changes."""

    async def async_ensure_setup(self) -> None:
        """Run _async_setup() once."""
        if self._setup_done:
            return
        await self._async_setup()
        self._setup_done = True

    async def async_poll(
        self, names: Iterable[str], report: UpdateReport | None = None
    ) -> UpdateReport:
        """Read each named sub-system and record what happened."""
        await self.async_ensure_setup()
        if report is None:
            report = UpdateReport()
        updated: list[str] = []
        for name in names:
            component = getattr(self, name)
            if component is None:
                continue
            try:
                await component.async_update(notify=False)
            except ModbusConnectionError:
                raise
            except ModbusTimeoutError as err:
                if not report.updated and not report.failed:
                    raise
                report.failed[name] = err
            except ModbusError as err:
                report.failed[name] = err
            else:
                report.updated.add(name)
                updated.append(name)
        for name in updated:
            getattr(self, name).notify()
        return report

    async def async_read_raw(self, names: Iterable[str]) -> dict:
        """Read the named sub-systems and return their raw maps merged."""
        await self.async_ensure_setup()
        raw: dict = {}
        for name in names:
            component = getattr(self, name)
            if component is None:
                continue
            part = await component.async_read_raw(notify=False)
            for space, addrs in part.items():
                raw.setdefault(space, {}).update(addrs)
        return dict(sorted((k, dict(sorted(v.items()))) for k, v in raw.items()))
