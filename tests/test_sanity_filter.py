"""Pruefung: Plausibilitaetsfilter."""
from __future__ import annotations

from custom_components.marstek_jupiter import const
from custom_components.marstek_jupiter.coordinator import JupiterCoordinator, JupiterData
from custom_components.marstek_jupiter.modbus import to_int16


def test_implausible_soc_rejected():
    data = JupiterData()
    store = JupiterCoordinator._store
    store(None, data, const.ADDR_BATTERY_SOC, [90])
    rejected = store(None, data, const.ADDR_BATTERY_SOC, [3308])
    assert rejected == 1
    assert data.registers[0x0010] == 90


def test_battery_voltage_zero_rejected():
    data = JupiterData()
    store = JupiterCoordinator._store
    store(None, data, const.ADDR_BATTERY_VOLTAGE, [530])
    store(None, data, const.ADDR_BATTERY_VOLTAGE, [0])
    assert data.registers[0x000F] == 530


def test_grid_import_passes():
    data = JupiterData()
    store = JupiterCoordinator._store
    store(None, data, const.ADDR_GRID_POWER, [65374])
    assert to_int16(data.registers[0x000D]) == -162


def test_temperature_below_five_degrees_passes():
    """Frostwerte muessen durchkommen.

    Bis 1.2.0b1 begann die Plausibilitaetsgrenze bei 5,0 Grad. Steht das
    Geraet kalt, wurde damit den ganzen Winter jeder Messwert verworfen,
    und der Sensor zeigte unbemerkt weiter den letzten Herbstwert.
    """
    data = JupiterData()
    store = JupiterCoordinator._store
    store(None, data, const.ADDR_TEMPERATURE, [180])
    rejected = store(None, data, const.ADDR_TEMPERATURE, [21])
    assert rejected == 0
    assert data.registers[0x000E] == 21


def test_temperature_outlier_still_rejected():
    data = JupiterData()
    store = JupiterCoordinator._store
    store(None, data, const.ADDR_TEMPERATURE, [180])
    rejected = store(None, data, const.ADDR_TEMPERATURE, [65500])
    assert rejected == 1
    assert data.registers[0x000E] == 180
