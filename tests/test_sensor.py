"""Tests for VARTA Modbus sensors."""

from types import SimpleNamespace

from custom_components.varta_modbus.sensor import (
    SENSORS,
    VartaSensor,
)


def _create_device():
    """Create fake VARTA device."""

    return SimpleNamespace(
        identity=SimpleNamespace(
            serial_number="VARTA123",
            software="1.0.0",
        ),
        battery=SimpleNamespace(
            state=SimpleNamespace(name="RUN"),
            active_power=500,
            charging_power=500,
            discharging_power=0,
            apparent_power=550,
            state_of_charge=87,
            ac_to_dc_energy=12345,
            installed_capacity=13500,
        ),
        grid=SimpleNamespace(
            power=-250,
        ),
    )


def _create_entry():
    """Create fake config entry."""

    return SimpleNamespace(
        entry_id="test_entry",
    )


def _create_coordinator(device):
    """Create fake coordinator."""

    return SimpleNamespace(
        device=device,
    )


def _create_sensor(key: str):
    """Create sensor by key."""

    device = _create_device()

    description = next(
        sensor
        for sensor in SENSORS
        if sensor.key == key
    )

    return VartaSensor(
        _create_coordinator(device),
        _create_entry(),
        description,
    )


def test_state_sensor_value():
    """Test enum state sensor."""

    sensor = _create_sensor("state")

    assert sensor.native_value == "run"


def test_active_power_sensor():
    """Test active power sensor."""

    sensor = _create_sensor("active_power")

    assert sensor.native_value == 500


def test_state_of_charge_sensor():
    """Test state of charge sensor."""

    sensor = _create_sensor("state_of_charge")

    assert sensor.native_value == 87


def test_grid_power_sensor():
    """Test grid power sensor."""

    sensor = _create_sensor("grid_power")

    assert sensor.native_value == -250


def test_unique_id():
    """Test unique id generation."""

    sensor = _create_sensor("state")

    assert sensor.unique_id == "VARTA123_state"


def test_device_info():
    """Test device information."""

    sensor = _create_sensor("state")

    assert sensor.device_info["manufacturer"] == "VARTA"
    assert sensor.device_info["serial_number"] == "VARTA123"


def test_enum_options():
    """Test state sensor options."""

    description = next(
        sensor
        for sensor in SENSORS
        if sensor.key == "state"
    )

    assert description.options == [
        "busy",
        "run",
        "charge",
        "discharge",
        "standby",
        "error",
        "service",
        "islanding",
    ]
