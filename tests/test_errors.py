"""Pruefung: ErrorWatcher."""
from __future__ import annotations

from homeassistant.helpers import issue_registry as ir

from custom_components.marstek_jupiter import const
from custom_components.marstek_jupiter.coordinator import BlockState, JupiterData
from custom_components.marstek_jupiter.errors import EVENT_ERROR, ErrorWatcher, issue_id


class _Bus:
    def __init__(self):
        self.events = []

    def async_fire(self, name, data):
        self.events.append((name, data))


class _Hass:
    bus = _Bus()


class _Coordinator:
    data = None


def _setup():
    hass = _Hass()
    hass.bus = _Bus()
    coordinator = _Coordinator()
    coordinator.data = JupiterData(blocks={b.key: BlockState() for b in const.BLOCKS})
    watcher = ErrorWatcher(hass, coordinator, "entry")
    block = const.block_for_address(const.ADDR_ERROR_CODE)
    key = ("marstek_jupiter", issue_id("entry"))
    return hass, coordinator, watcher, block, key


def test_no_fresh_block_no_issue():
    hass, coordinator, watcher, block, key = _setup()
    coordinator.data.registers[const.ADDR_ERROR_CODE] = 1062
    watcher.async_check()
    assert key not in ir.ISSUES


def test_clean_start_no_event():
    hass, coordinator, watcher, block, key = _setup()
    coordinator.data.blocks[block].last_success = 1.0
    coordinator.data.registers[const.ADDR_ERROR_CODE] = 0
    watcher.async_check()
    assert hass.bus.events == []


def test_error_creates_issue():
    hass, coordinator, watcher, block, key = _setup()
    coordinator.data.blocks[block].last_success = 1.0
    coordinator.data.registers[const.ADDR_ERROR_CODE] = 0
    watcher.async_check()
    coordinator.data.registers[const.ADDR_ERROR_CODE] = 1062
    watcher.async_check()
    assert key in ir.ISSUES
    assert ir.ISSUES[key]["translation_placeholders"]["code_hex"] == "0x426"
    assert [(n, d["active"], d["code"]) for n, d in hass.bus.events] == [(EVENT_ERROR, True, 1062)]


def test_same_code_no_duplicate_event():
    hass, coordinator, watcher, block, key = _setup()
    coordinator.data.blocks[block].last_success = 1.0
    coordinator.data.registers[const.ADDR_ERROR_CODE] = 0
    watcher.async_check()
    coordinator.data.registers[const.ADDR_ERROR_CODE] = 1062
    watcher.async_check()
    watcher.async_check()
    assert len(hass.bus.events) == 1


def test_cleared_removes_issue():
    hass, coordinator, watcher, block, key = _setup()
    coordinator.data.blocks[block].last_success = 1.0
    coordinator.data.registers[const.ADDR_ERROR_CODE] = 0
    watcher.async_check()
    coordinator.data.registers[const.ADDR_ERROR_CODE] = 1062
    watcher.async_check()
    coordinator.data.registers[const.ADDR_ERROR_CODE] = 0
    watcher.async_check()
    assert key not in ir.ISSUES
    assert hass.bus.events[-1][1]["active"] is False
    assert hass.bus.events[-1][1]["previous_code"] == 1062


def test_retired_entities():
    from custom_components.marstek_jupiter import RETIRED_KEYS
    from custom_components.marstek_jupiter import sensor as sn
    keys = {d.key for d in sn.SENSORS}
    assert not sorted(keys & set(RETIRED_KEYS))
    assert len(RETIRED_KEYS) == 8
