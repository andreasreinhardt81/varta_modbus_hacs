# VARTA Modbus for Home Assistant

A Home Assistant custom integration for VARTA energy-storage systems using Modbus TCP and the modern shared Modbus connection API.

This project intentionally uses the integration domain **`varta_modbus`** and the display name **VARTA Modbus**. It is separate from the older `varta_storage` integration so both integrations can be distinguished during community testing.

The VARTA device-library source is vendored under `custom_components/varta_modbus/vendor/varta_modbus` so testers exercise the same register model that is intended for the standalone library and future upstream contribution.

## Installation with HACS

1. Add this repository as a custom integration repository in HACS.
2. Install **VARTA Modbus**.
3. Restart Home Assistant.
4. Go to **Settings → Devices & services → Add integration**.
5. Search for **VARTA Modbus**.
6. Enter the VARTA device host, TCP port (default `502`) and Modbus unit ID (default `1`).

### Important: existing VARTA Storage integration

The older integration using the domain `varta_storage` is a different integration. Do not install both integrations for the same battery at the same time unless you deliberately want both to poll the device.

If you previously installed the older integration, remove its config entry and custom-component files before switching to **VARTA Modbus**.

## Exposed values

The integration exposes battery state, signed active/apparent power, separate charging/discharging power, state of charge, AC→DC energy, installed capacity, signed grid power, and diagnostic software/identity values.

The device model preserves the timing from the VARTA community workaround: 250 ms per-unit request spacing, a 3 s minimum timeout, and a 1 s connect delay.

## Writable power limits

Two Home Assistant number entities write VARTA holding registers directly:

- **1074 – Maximum discharging power:** signed `int16`; VARTA uses negative values, e.g. `-4000` for a 4 kW discharge limit.
- **1075 – Maximum charging power:** signed `int16`; VARTA uses positive values, e.g. `4000` for a 4 kW charge limit.

## Development

The repository follows the Home Assistant integration blueprint pattern and uses the modern `async_get_unit` / `async_get_temporary_unit` Modbus API.

Run `scripts/lint` for Ruff checks and `scripts/test` for the test suite in a suitable Home Assistant custom-component development environment.

## Uploading the repository to GitHub

Extract the ZIP locally first; GitHub does not unpack a ZIP uploaded through the web UI. The easiest method is GitHub Desktop: add the extracted `varta_modbus_hacs` folder as a local repository, then choose **Publish repository**. Alternatively, from a terminal in the extracted folder:

```bash
git init
git add .
git commit -m "Initial VARTA Modbus HACS integration"
git branch -M main
git remote add origin https://github.com/andreasreinhardt81/varta_modbus_hacs.git
git push -u origin main
```

For a custom integration, translations belong in `custom_components/varta_modbus/translations/en.json`; `strings.json` is intentionally not included.
