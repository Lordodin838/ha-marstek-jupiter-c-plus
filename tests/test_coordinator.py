"""Pruefung: Coordinator, Energiezaehler, always_update."""
from __future__ import annotations

import pytest

from custom_components.marstek_jupiter import const
from custom_components.marstek_jupiter.coordinator import (
    ENERGY_CHARGE,
    ENERGY_DISCHARGE,
    ENERGY_PV,
    BlockState,
    JupiterCoordinator,
    JupiterData,
)


def _make():
    coordinator = JupiterCoordinator(
        None, None, config_entry=None, fast_interval=10,
        slow_interval=60, status_interval=300, static_interval=3600,
        entry_title="Test",
    )
    data = JupiterData(blocks={b.key: BlockState() for b in const.BLOCKS})
    return coordinator, data


def _round(coordinator, data, now, pv, grid, fresh=True):
    for n, address in enumerate(const.ADDR_PV_POWER):
        data.registers[address] = pv[n]
    data.registers[const.ADDR_GRID_POWER] = grid & 0xFFFF
    for key in ("fast_a", "fast_b"):
        if fresh:
            data.blocks[key].last_success = now
    coordinator._integrate_energy(data, now)


def test_always_update():
    coordinator, _ = _make()
    assert coordinator.always_update is True


def test_pv_charge_one_hour():
    coordinator, data = _make()
    for step in range(361):
        _round(coordinator, data, step * 10.0, (250, 250, 250, 250), 400)
    assert round(data.energy[ENERGY_PV], 3) == 1.0
    assert round(data.energy[ENERGY_CHARGE], 3) == 0.6
    assert data.energy[ENERGY_DISCHARGE] == 0.0


def test_discharge_one_hour():
    coordinator, data = _make()
    for step in range(361):
        _round(coordinator, data, step * 10.0, (0, 0, 0, 0), 500)
    assert round(data.energy[ENERGY_DISCHARGE], 3) == 0.5
    assert data.energy[ENERGY_CHARGE] == 0.0


def test_grid_import_charges():
    coordinator, data = _make()
    for step in range(361):
        _round(coordinator, data, step * 10.0, (0, 0, 0, 0), -200)
    assert round(data.energy[ENERGY_CHARGE], 3) == 0.2


def test_stale_round_not_counted():
    coordinator, data = _make()
    _round(coordinator, data, 0.0, (250, 250, 250, 250), 0)
    _round(coordinator, data, 10.0, (250, 250, 250, 250), 0, fresh=False)
    assert data.energy[ENERGY_PV] == 0.0


def test_gap_not_bridged():
    coordinator, data = _make()
    _round(coordinator, data, 0.0, (250, 250, 250, 250), 0)
    _round(coordinator, data, 600.0, (250, 250, 250, 250), 0)
    assert data.energy[ENERGY_PV] == 0.0
    _round(coordinator, data, 610.0, (250, 250, 250, 250), 0)
    assert round(data.energy[ENERGY_PV] * 3600, 3) == round(10 / 1000 * 1000, 3)


def test_request_budget():
    per_minute = 0.0
    intervals = {
        const.TIER_FAST: const.DEFAULT_FAST_INTERVAL,
        const.TIER_SLOW: const.DEFAULT_SLOW_INTERVAL,
        const.TIER_STATUS: const.DEFAULT_STATUS_INTERVAL,
        const.TIER_STATIC: const.DEFAULT_STATIC_INTERVAL,
    }
    for block in const.BLOCKS:
        per_minute += 60 / intervals[block.tier]
    assert per_minute < 20, f"Buslast {per_minute:.1f} >= 20 Anfragen/Minute"
