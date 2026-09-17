"""Constants for the VARTA Modbus integration."""

from __future__ import annotations

DOMAIN = "varta_modbus"

CONF_UNIT_ID = "unit_id"

DEFAULT_PORT = 502
DEFAULT_UNIT_ID = 1

# VARTA external power-control watchdog.
#
# Writing register 1074 or 1075 starts a 120 second timeout.
# Refresh the active limits every 60 seconds.
VARTA_EXTERNAL_CONTROL_TIMEOUT = 120
