"""Pruefung: Energie-Sensor Restore."""
from __future__ import annotations

import pytest

from custom_components.marstek_jupiter import sensor as sn
from custom_components.marstek_jupiter.coordinator import ENERGY_PV, JupiterData


class _Last:
    native_value = "43.419"


class _Coordinator:
    last_update_success = True
    data = None


@pytest.mark.asyncio
async def test_energy_restore():
    coordinator = _Coordinator()
    coordinator.data = JupiterData()
    coordinator.data.energy[ENERGY_PV] = 0.25

    description = next(d for d in sn.ENERGY_SENSORS if d.key == ENERGY_PV)
    sensor = sn.JupiterEnergySensor(coordinator, "entry", description)
    sensor._last_sensor_data = _Last()
    await sensor.async_added_to_hass()

    assert sensor.native_value == 43.419
    coordinator.data.energy[ENERGY_PV] += 0.1
    assert sensor.native_value == 43.519


def test_energy_sensor_metadata():
    description = next(d for d in sn.ENERGY_SENSORS if d.key == ENERGY_PV)
    assert description.state_class == "total_increasing"
    assert description.native_unit_of_measurement == "kWh"
    assert description.device_class == "energy"


# ---------------------------------------------------------------------------
# Fehlercode-Klartext: nur noch Modbus, keine zweite Quelle
# ---------------------------------------------------------------------------

class _Entry:
    entry_id = "entry"
    options: dict = {}
    data: dict = {}


def _error_sensor(register_value):
    coordinator = _Coordinator()
    coordinator.data = JupiterData()
    if register_value is not None:
        coordinator.data.registers[0x0011] = register_value
    return sn.JupiterErrorTextSensor(coordinator, _Entry(), {})


def test_error_text_from_register():
    # 1062 dezimal = 0x426, der im Handbuch fehlende Code.
    sensor = _error_sensor(1062)
    assert "0x426" in sensor.native_value


def test_error_text_zero_means_no_error():
    sensor = _error_sensor(0)
    assert sensor.native_value == "kein Fehler"


def test_error_text_has_no_second_source():
    """Der MQTT-Fallback ist seit 1.2.0b2 entfernt.

    Weder darf ein hinterlegter Eintrag noch ausgewertet werden, noch
    darf das Attribut fallback_entity zurueckkommen - sonst stimmt die
    Zusage "ausschliesslich ueber Modbus" nicht.
    """
    entry = _Entry()
    entry.options = {"error_fallback": "sensor.irgendwas"}
    coordinator = _Coordinator()
    coordinator.data = JupiterData()
    coordinator.data.registers[0x0011] = 0
    sensor = sn.JupiterErrorTextSensor(coordinator, entry, {})

    assert sensor.native_value == "kein Fehler"
    assert "fallback_entity" not in sensor.extra_state_attributes
    assert not hasattr(sensor, "_fallback_entity")
