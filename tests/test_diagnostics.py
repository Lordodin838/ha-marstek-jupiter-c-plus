"""Tests fuer diagnostics.py.

Prueft:
  - Ausgabe-Struktur (alle Pflichtschluessel vorhanden)
  - Kein Host im Dump (Datenschutz)
  - Register korrekt formatiert (0x-Hex-Keys)
  - Energie gerundet
  - Keine PII: keine IP-Adresse im Dump
  - data=None haengt nicht
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.marstek_jupiter import const
from custom_components.marstek_jupiter.coordinator import BlockState, JupiterData
from custom_components.marstek_jupiter.diagnostics import (
    async_get_config_entry_diagnostics,
)


def _make_entry(data: JupiterData | None, host: str = "192.168.1.100"):
    """Baut ein minimales ConfigEntry-Mock fuer den Diagnostics-Test."""
    coordinator = MagicMock()
    coordinator.data = data

    runtime_data = SimpleNamespace(
        coordinator=coordinator,
        adopted_entity_ids=["sensor.jupiter_pv_leistung"],
    )

    entry = MagicMock()
    entry.data = {"host": host}
    entry.options = {"fast_interval": 10, "slow_interval": 60}
    entry.runtime_data = runtime_data
    return entry


def _make_data(registers: dict | None = None) -> JupiterData:
    blocks = {b.key: BlockState(last_success=1.0, failures=0) for b in const.BLOCKS}
    data = JupiterData(
        registers=registers or {0x0001: 363, 0x0009: 162},
        blocks=blocks,
        rejected=2,
        requests=100,
    )
    data.energy["pv_energy"] = 1.23456789
    return data


@pytest.mark.asyncio
async def test_top_level_keys_present():
    entry = _make_entry(_make_data())
    result = await async_get_config_entry_diagnostics(None, entry)
    for key in ("konfiguration", "bloecke", "register", "verworfene_werte",
                "anfragen_gesamt", "energie_seit_start_kwh", "uebernommene_entity_ids"):
        assert key in result, f"Schluessel fehlt: {key}"


@pytest.mark.asyncio
async def test_host_not_in_dump():
    """IP-Adresse darf nicht im Dump erscheinen."""
    entry = _make_entry(_make_data(), host="192.168.1.100")
    result = await async_get_config_entry_diagnostics(None, entry)
    dump_str = str(result)
    assert "192.168.1.100" not in dump_str
    assert result["konfiguration"]["host_gesetzt"] is True


@pytest.mark.asyncio
async def test_register_keys_hex_format():
    """Register-Keys muessen als 0xXXXX formatiert sein."""
    data = _make_data({0x0001: 363, 0x0011: 1062})
    entry = _make_entry(data)
    result = await async_get_config_entry_diagnostics(None, entry)
    for key in result["register"]:
        assert key.startswith("0x"), f"Register-Key nicht in Hex: {key}"
        assert len(key) == 6, f"Register-Key falsche Laenge: {key}"


@pytest.mark.asyncio
async def test_energie_rounded():
    """Energiewerte werden auf 4 Nachkommastellen gerundet."""
    data = _make_data()
    data.energy["pv_energy"] = 1.23456789
    entry = _make_entry(data)
    result = await async_get_config_entry_diagnostics(None, entry)
    pv = result["energie_seit_start_kwh"]["pv_energy"]
    assert pv == round(1.23456789, 4)


@pytest.mark.asyncio
async def test_all_blocks_present():
    """Jeder BLOCK muss einen Eintrag in 'bloecke' haben."""
    entry = _make_entry(_make_data())
    result = await async_get_config_entry_diagnostics(None, entry)
    for block in const.BLOCKS:
        assert block.key in result["bloecke"], f"Block fehlt: {block.key}"


@pytest.mark.asyncio
async def test_block_entry_has_required_keys():
    entry = _make_entry(_make_data())
    result = await async_get_config_entry_diagnostics(None, entry)
    for key, block_info in result["bloecke"].items():
        for field in ("bereich", "takt", "fehlversuche", "letzter_erfolg", "exception"):
            assert field in block_info, f"Block '{key}': Feld '{field}' fehlt"


@pytest.mark.asyncio
async def test_data_none_does_not_crash():
    """Wenn noch kein Coordinator-Datensatz vorliegt, darf kein Fehler kommen."""
    entry = _make_entry(None)
    result = await async_get_config_entry_diagnostics(None, entry)
    assert result["register"] == {}
    assert result["verworfene_werte"] is None
    assert result["anfragen_gesamt"] is None
    assert result["energie_seit_start_kwh"] == {}


@pytest.mark.asyncio
async def test_adopted_entity_ids_forwarded():
    entry = _make_entry(_make_data())
    result = await async_get_config_entry_diagnostics(None, entry)
    assert result["uebernommene_entity_ids"] == ["sensor.jupiter_pv_leistung"]
