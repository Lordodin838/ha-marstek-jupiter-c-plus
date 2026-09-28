"""Tests fuer services.py – isolierbare Hilfsfunktionen."""
from __future__ import annotations

import asyncio
import pytest

from custom_components.marstek_jupiter.services import (
    _decode,
    _majority,
    _runs,
    _probe,
    _discover,
)
from simulator import JupiterSimulator
from custom_components.marstek_jupiter.modbus import JupiterModbusClient


# ---------------------------------------------------------------------------
# _majority
# ---------------------------------------------------------------------------

def test_majority_all_same():
    assert _majority([5, 5, 5]) == (5, True)

def test_majority_two_of_three():
    assert _majority([5, 5, 7]) == (5, True)

def test_majority_no_majority():
    # alle verschieden → kein Wert hat ≥2 Treffer
    value, sure = _majority([1, 2, 3])
    assert not sure

def test_majority_all_none():
    assert _majority([None, None]) == (None, False)

def test_majority_mixed_none():
    # zwei echte Werte, einer None → 1 von 2 ist kein Mehrheitswert
    value, sure = _majority([None, 42, 42])
    assert value == 42
    assert sure is True

def test_majority_single():
    # Ein einziger Wert: kein zweiter Zeuge → nicht sicher
    value, sure = _majority([99])
    assert value == 99
    assert sure is False


# ---------------------------------------------------------------------------
# _runs
# ---------------------------------------------------------------------------

def test_runs_empty():
    assert _runs([]) == []

def test_runs_single():
    assert _runs([5]) == [[5]]

def test_runs_consecutive():
    assert _runs([0, 1, 2, 3]) == [[0, 1, 2, 3]]

def test_runs_gap():
    assert _runs([0, 1, 5, 6]) == [[0, 1], [5, 6]]

def test_runs_max_chunk():
    # Nach 8 Registern muss ein neuer Chunk beginnen (MAX_REGISTERS = 8)
    addrs = list(range(16))
    result = _runs(addrs)
    assert len(result) == 2
    assert result[0] == list(range(8))
    assert result[1] == list(range(8, 16))

def test_runs_isolated():
    assert _runs([0, 2, 4]) == [[0], [2], [4]]


# ---------------------------------------------------------------------------
# _decode
# ---------------------------------------------------------------------------

def test_decode_raw():
    assert _decode([1, 2, 3], "raw") == [1, 2, 3]

def test_decode_int16_negative():
    assert _decode([0xFFFF], "int16") == [-1]

def test_decode_uint32():
    # 0x0001_0000
    assert _decode([0x0001, 0x0000], "uint32") == [65536]

def test_decode_string():
    # 'AB' = 0x4142
    assert _decode([0x4142], "string") == "AB"

def test_decode_unknown_falls_back():
    # unbekannter Typ → rohe Liste
    assert _decode([7], "unknown_type") == [7]


# ---------------------------------------------------------------------------
# _probe / _discover gegen Simulator
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_probe_valid_address():
    sim = JupiterSimulator()
    port = await sim.start()
    client = JupiterModbusClient("127.0.0.1", port, timeout=2, message_wait=0.01)
    try:
        result = await _probe(client, 0x0001, 1)
        assert result is not None
        assert len(result) == 1
    finally:
        await client.close()
        await sim.stop()

@pytest.mark.asyncio
async def test_probe_invalid_address_returns_none():
    sim = JupiterSimulator()
    port = await sim.start()
    client = JupiterModbusClient("127.0.0.1", port, timeout=2, message_wait=0.01)
    try:
        # 0x0500 liegt ausserhalb der gueltigen Bereiche des Simulators
        result = await _probe(client, 0x0500, 1)
        assert result is None
    finally:
        await client.close()
        await sim.stop()

@pytest.mark.asyncio
async def test_discover_finds_known_range():
    sim = JupiterSimulator()
    port = await sim.start()
    client = JupiterModbusClient("127.0.0.1", port, timeout=2, message_wait=0.01)
    try:
        # Der Datenblock 0x0000–0x003F ist im Simulator gueltig
        found = await _discover(client, 0x0001, 0x003F)
        assert len(found) > 0
        assert all(0x0001 <= a <= 0x003F for a in found)
    finally:
        await client.close()
        await sim.stop()
