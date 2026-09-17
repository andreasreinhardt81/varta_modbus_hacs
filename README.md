# VARTA Modbus

Home Assistant custom integration for VARTA energy-storage systems using Modbus TCP and the modern Home Assistant shared Modbus connection API.

This integration provides read access to battery and grid data as well as write access to selected VARTA power-limit registers.

> This project uses the integration domain `varta_modbus` and display name `VARTA Modbus`.
>
> It is intentionally separate from the older `varta_storage` integration in order to evaluate and validate a modern implementation based on the current Home Assistant Modbus architecture.

---

## Features

### Battery Monitoring

The integration exposes:

- Operating state
- Active power
- Apparent power
- Charging power
- Discharging power
- State of charge (SOC)
- AC-to-DC energy
- Installed battery capacity

### Grid Monitoring

- Grid power

### Diagnostic Information

- Installed battery modules
- Register table version
- EMS software version
- ENS software version
- Main software version
- Watchdog Timeout

### Writable Power Control

- Direct access to charging limit register 1075
- Direct access to discharging limit register 1074
- Compatible with Home Assistant automations
- Suitable for dynamic energy management systems

---

## Requirements

- Home Assistant 2026.9 or newer
- VARTA energy-storage system with Modbus TCP support
- Network connectivity between Home Assistant and the storage system

Default values:

| Parameter | Default |
|------------|---------|
| Port | 502 |
| Unit ID | 1 |

---

## Installation

### HACS

1. Open HACS.
2. Select **Integrations**.
3. Open **Custom repositories**.
4. Add this repository as an **Integration** repository.
5. Search for **VARTA Modbus**.
6. Install the integration.
7. Restart Home Assistant.

### Manual Installation

Copy

```text
custom_components/varta_modbus
```

to

```text
config/custom_components/
```

Restart Home Assistant and add the integration via:

```text
Settings → Devices & Services → Add Integration
```

---

## Configuration

The integration supports full UI configuration through Home Assistant Config Flow.

Enter:

- Host name or IP address
- TCP port
- Modbus unit ID

The connection is validated during configuration.

Configuration can later be modified using the Home Assistant **Reconfigure** function.

---

## Available Entities

### Sensors

| Entity | Description |
|----------|-------------|
| State | Operating state |
| Active Power | Battery active power |
| Charging Power | Current charging power |
| Discharging Power | Current discharging power |
| Apparent Power | Battery apparent power |
| State of Charge | Battery state of charge |
| AC to DC Energy | Energy counter |
| Installed Capacity | Installed battery capacity |
| Grid Power | Current grid power |

### Diagnostic Sensors

| Entity | Description |
|----------|-------------|
| Installed Battery Modules | Number of installed modules |
| Table Version | VARTA register table version |
| EMS Software | EMS firmware version |
| ENS Software | ENS firmware version |
| Software | Main firmware version |

### Configuration Entities

| Entity | Description |
|----------|-------------|
| Maximum Charging Power | Writable charging limit |
| Maximum Discharging Power | Writable discharge limit |

---

## Operating States

The integration currently reports the following VARTA operating states:

| State | Description |
|----------|-------------|
| Busy | Device processing |
| Running | Normal operation |
| Charging | Battery charging |
| Discharging | Battery discharging |
| Standby | Standby mode |
| Error | Fault condition |
| Service | Service mode |
| Islanding | Island operation |

---

## Writable Power Limits

The integration provides direct access to the following writable VARTA registers:

| Register | Function |
|----------|----------|
| 1074 | Maximum discharging power |
| 1075 | Maximum charging power |

### Register Values

VARTA internally uses signed values:

| Operation | Example |
|----------|----------|
| Charging | +4000 W |
| Discharging | -4000 W |

Examples:

```text
+4000 = charging limited to 4 kW
-4000 = discharging limited to 4 kW
```

The integration automatically handles the VARTA sign conventions.

---

## 500 W Limitation

Many VARTA storage systems enforce a minimum charging or discharging limit of **500 W**.

Maximum discharge:
0 W or <= -500 W

Maximum charge:
0 W or >= 500 W

These values are checked.

---

## VARTA Watchdog Behaviour

Writing registers 1074 or 1075 starts VARTA's 120 second
external-control timeout in register 1073.

While an external power limit is active, VARTA Modbus refreshes
the configured value every 60 seconds to prevent the device from
reverting to its internal default.

---

## Migration from varta_storage

The older integration uses the domain:

```text
varta_storage
```

This integration uses:

```text
varta_modbus
```

Both integrations are independent and can coexist technically, but running both against the same battery is generally not recommended.

Migration procedure:

1. Remove the old integration.
2. Remove the old custom component files.
3. Install VARTA Modbus.
4. Create a new configuration entry.

---

## Technical Notes

This integration is based on modern Home Assistant integration concepts:

- Config Flow
- Reconfigure Flow
- Update Coordinator
- Shared Home Assistant Modbus connection API
- Diagnostics Support
- Entity Translations
- Unique IDs
- Device Registry
- Writable Modbus Registers

The bundled VARTA device model preserves the timing behaviour used by the established VARTA community workaround implementation:

- 250 ms request spacing
- 3 s minimum timeout
- 1 s connect delay

---

## Diagnostics

The integration supports Home Assistant Diagnostics.

When diagnostics are exported:

- IP addresses are redacted
- Serial numbers are redacted

This allows safe sharing of diagnostic information when reporting issues.

---

## Troubleshooting

### Connection cannot be established

Verify:

- Modbus TCP is enabled on the VARTA system
- Correct IP address or hostname
- Correct TCP port
- Correct Unit ID
- Firewall settings

### Data does not update

Verify:

- Network connectivity
- Device availability
- Home Assistant logs

### Power limits are not applied

Verify:

- Requested value exceeds the firmware minimum threshold
- Watchdog requirements are fulfilled
- Storage system firmware supports external power control

---

## Contributing

Contributions are welcome.

Please read:

```text
CONTRIBUTING.md
```

before creating pull requests.

---

## Disclaimer

This project is not affiliated with, endorsed by, or sponsored by VARTA AG.

Use at your own risk.
