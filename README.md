[🇬🇧 English](README.md) | [🇩🇪 Deutsch](README_de.md)

# VARTA Modbus

[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2026.9%2B-green.svg)](https://www.home-assistant.io/)

Home Assistant custom integration for VARTA energy-storage systems using Modbus TCP and the modern Home Assistant shared Modbus connection architecture.

This integration provides:

- Battery monitoring
- Grid monitoring
- Writable power limits
- Diagnostics support
- Native Home Assistant Config Flow
- Reconfigure Flow
- Shared Modbus connections
- Full translation support

The integration domain is:

```text
varta_modbus
```

This project is intentionally separate from the older:

```text
varta_storage
```

implementation and is based on current Home Assistant integration standards.

---

# Features

## Battery Monitoring

The integration provides the following battery information:

- Operating state
- Active power
- Apparent power
- Charging power
- Discharging power
- State of charge (SOC)
- AC-to-DC energy
- Installed capacity

## Grid Monitoring

- Grid power

## Diagnostic Information

- Installed battery modules
- Register table version
- EMS software version
- ENS software version
- Main software version
- Watchdog timeout

## Writable Power Control

Direct access to the following VARTA registers:

| Register | Description |
|----------|-------------|
| 1074 | Maximum discharging power |
| 1075 | Maximum charging power |

Supported use cases:

- Dynamic electricity tariffs
- PV surplus charging
- Energy management systems (EMS)
- Peak shaving
- Grid export limitation

---

# Requirements

- Home Assistant 2026.9 or newer
- VARTA energy storage system with Modbus TCP access
- Network connectivity between Home Assistant and the VARTA system

Default values:

| Parameter | Default |
|----------|---------|
| Port | 502 |
| Unit ID | 1 |

---

# Installation

## HACS

1. Open HACS
2. Select **Integrations**
3. Open **Custom repositories**
4. Add this repository as an **Integration**
5. Search for **VARTA Modbus**
6. Install
7. Restart Home Assistant

## Manual Installation

Copy:

```text
custom_components/varta_modbus
```

to:

```text
config/custom_components/
```

Restart Home Assistant and add the integration via:

```text
Settings → Devices & Services → Add Integration
```

---

# Configuration

Configuration is performed entirely via Home Assistant UI.

Required settings:

| Parameter | Description |
|----------|-------------|
| Host | VARTA IP address or hostname |
| Port | Modbus TCP port |
| Unit ID | Modbus unit identifier |

Configuration is validated before it is saved.

After setup, configuration can be changed using Home Assistant's built-in **Reconfigure** functionality.

---

# Available Entities

## Sensors

| Entity | Description |
|----------|-------------|
| State | Current operating state |
| Active Power | Active battery power |
| Charging Power | Current charge power |
| Discharging Power | Current discharge power |
| Apparent Power | Apparent battery power |
| State of Charge | Battery charge level |
| AC to DC Energy | Energy counter |
| Installed Capacity | Installed battery capacity |
| Grid Power | Grid power |

## Diagnostic Sensors

| Entity | Description |
|----------|-------------|
| Installed Battery Modules | Installed module count |
| Table Version | Register table version |
| EMS Software | EMS version |
| ENS Software | ENS version |
| Software | Main firmware version |

## Writable Number Entities

| Entity | Description |
|----------|-------------|
| Maximum Charging Power | Writable charging limit |
| Maximum Discharging Power | Writable discharge limit |

---

# Operating States

| State | Description |
|----------|-------------|
| Busy | Processing |
| Running | Normal operation |
| Charging | Battery charging |
| Discharging | Battery discharging |
| Standby | Standby mode |
| Error | Error condition |
| Service | Service mode |
| Islanding | Island operation |

---

# Writable Power Limits

The integration supports writing:

| Register | Function |
|----------|----------|
| 1074 | Maximum discharging power |
| 1075 | Maximum charging power |

## Register Sign Convention

VARTA internally uses signed values:

| Operation | Example |
|----------|---------|
| Charging | +4000 W |
| Discharging | -4000 W |

Examples:

```text
+4000 = charging limited to 4 kW
-4000 = discharging limited to 4 kW
```

---

# 500 W Limitation

Most VARTA firmware versions enforce minimum charge/discharge limits.

Accepted values are typically:

```text
Maximum discharge:
0 W
or <= -500 W

Maximum charge:
0 W
or >= 500 W
```

Values between these thresholds may be rejected by the storage system.

The integration validates these limits before writing.

---

# Watchdog Behaviour

Writing register 1074 or 1075 activates VARTA's external control watchdog.

Relevant registers:

| Register | Function |
|----------|----------|
| 1073 | Watchdog timeout |
| 1074 | Maximum discharge limit |
| 1075 | Maximum charge limit |

Current implementation:

- VARTA watchdog timeout: 120 seconds
- Automatic refresh interval: 60 seconds

As long as an external limit is active, VARTA Modbus automatically refreshes the configured values to prevent the storage system from reverting to its internal defaults.

---
