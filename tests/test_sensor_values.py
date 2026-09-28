"""Pruefung: Sensorwerte gegen echte Messwerte."""
from __future__ import annotations

from custom_components.marstek_jupiter import sensor as sn
from custom_components.marstek_jupiter.coordinator import JupiterData
from simulator import REGISTERS


def test_sensor_values():
    data = JupiterData(registers=dict(REGISTERS))
    values = {d.key: d.value_fn(data) for d in sn.SENSORS}

    assert values["pv1_voltage"] == 36.3
    assert values["pv2_power"] == 3
    assert values["pv_total_power"] == 3
    assert values["grid_power"] == 162
    assert values["battery_voltage"] == 53.0
    assert values["battery_soc"] == 90
    assert values["daily_generation"] == 5.75
    assert values["monthly_generation"] == 31.67
    assert values["daily_grid"] == 3.94
    assert values["monthly_grid"] == 29.46
    assert values["cell_voltage_max"] == 3.317
    assert values["cell_voltage_delta"] == 2
    assert values["temperature"] == 28.0
    assert values["device_type_text"] == "Jupiter C 800 W"
    assert values["ems_version"] == 142
    assert values["mac_address"] == "24215ee5674d"
    # PV 3 W, Netz 162 W Abgabe -> 159 W aus der Batterie
    assert values["battery_power"] == -159
    assert values["battery_charge_power"] == 0
    assert values["battery_discharge_power"] == 159
