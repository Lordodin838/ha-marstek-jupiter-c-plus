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
