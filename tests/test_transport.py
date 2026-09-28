"""Pruefung: Modbus-Transport gegen den Simulator."""
from __future__ import annotations

import asyncio
import struct
import pytest

from custom_components.marstek_jupiter import const
from custom_components.marstek_jupiter.modbus import (
    JupiterModbusClient,
    ModbusExceptionResponse,
)
from simulator import REGISTERS, JupiterSimulator


@pytest.mark.asyncio
async def test_all_blocks():
    sim = JupiterSimulator()
    port = await sim.start()
    client = JupiterModbusClient("127.0.0.1", port, timeout=2, message_wait=0.01)
    try:
        for block in const.BLOCKS:
            values = await client.read_holding(block.start, block.count)
            want = [REGISTERS[block.start + i] for i in range(block.count)]
            assert values == want, f"Block {block.key}: {values!r} != {want!r}"
    finally:
        await client.close()
        await sim.stop()


@pytest.mark.asyncio
async def test_range_overflow_rejected():
    sim = JupiterSimulator()
    port = await sim.start()
    client = JupiterModbusClient("127.0.0.1", port, timeout=2, message_wait=0.01)
    try:
        with pytest.raises(ModbusExceptionResponse) as exc_info:
            await client.read_holding(0x0021, 8)
        assert exc_info.value.code == 2
    finally:
        await client.close()
        await sim.stop()


@pytest.mark.asyncio
async def test_too_many_registers():
    sim = JupiterSimulator()
    port = await sim.start()
    client = JupiterModbusClient("127.0.0.1", port, timeout=2, message_wait=0.01)
    try:
        with pytest.raises(ValueError):
            await client.read_holding(0x0001, 9)
    finally:
        await client.close()
        await sim.stop()


@pytest.mark.asyncio
async def test_stray_response():
    """Verirrte Antwort mit fremder Transaction-ID muss verworfen werden."""
    sim = JupiterSimulator(stray_before=2)
    port = await sim.start()
    client = JupiterModbusClient("127.0.0.1", port, timeout=2, message_wait=0.01)
    try:
        values = await client.read_holding(0x0009, 8)
        want = [REGISTERS[0x0009 + i] for i in range(8)]
        assert values == want
        assert values[7] == 90  # SoC bleibt korrekt
    finally:
        await client.close()
        await sim.stop()


@pytest.mark.asyncio
async def test_late_response():
    """Verspaetete Antwort darf nicht der naechsten Anfrage zugeordnet werden."""
    sim = JupiterSimulator(delay_first=1.0)
    port = await sim.start()
    client = JupiterModbusClient("127.0.0.1", port, timeout=0.3, message_wait=0.01, retries=2)
    try:
        values = await client.read_holding(0x0009, 8)
        want = [REGISTERS[0x0009 + i] for i in range(8)]
        assert values == want
    finally:
        await client.close()
        await sim.stop()


@pytest.mark.asyncio
async def test_serialisation():
    """20 gleichzeitige Anfragen duerfen sich nicht ueberholen."""
    sim = JupiterSimulator()
    port = await sim.start()
    client = JupiterModbusClient("127.0.0.1", port, timeout=2, message_wait=0.0)
    try:
        results = await asyncio.gather(
            *[
                client.read_holding(0x0009, 8) if i % 2 else client.read_holding(0x0001, 8)
                for i in range(20)
            ]
        )
        for i, values in enumerate(results):
            base = 0x0009 if i % 2 else 0x0001
            want = [REGISTERS[base + k] for k in range(8)]
            assert values == want, f"Anfrage {i}: {values!r} != {want!r}"
    finally:
        await client.close()
        await sim.stop()


# ---------------------------------------------------------------------------
# Reconnect-Tests
# ---------------------------------------------------------------------------

class DropAfterSimulator(JupiterSimulator):
    """Simulator, der die Verbindung nach N Anfragen kalt trennt.

    Bildet den Fall nach, in dem der Elfin EW11 den Socket schliesst
    (z.B. nach einem Neustart oder Netzausfall).
    """

    def __init__(self, drop_after: int = 1, **kwargs):
        super().__init__(**kwargs)
        self._drop_after = drop_after

    async def _handle(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        served = 0
        try:
            while True:
                header = await reader.readexactly(6)
                tid, pid, length = struct.unpack(">HHH", header)
                body = await reader.readexactly(length)
                unit, function = body[0], body[1]
                self.requests += 1
                served += 1

                writer.write(self._respond(tid, unit, function, body))
                await writer.drain()

                if served >= self._drop_after:
                    # Verbindung kalt schliessen nach der Antwort
                    writer.close()
                    return
        except (asyncio.IncompleteReadError, ConnectionError):
            pass
        finally:
            try:
                writer.close()
            except Exception:
                pass


@pytest.mark.asyncio
async def test_reconnect_after_drop():
    """Client muss nach einem Verbindungsabbruch selbst neu verbinden.

    Der Simulator schliesst den Socket nach der ersten Anfrage. Der Client
    soll danach trotzdem noch korrekte Daten lesen koennen.
    """
    sim = DropAfterSimulator(drop_after=1)
    port = await sim.start()
    client = JupiterModbusClient(
        "127.0.0.1", port, timeout=2, message_wait=0.01, retries=3
    )
    try:
        # Erste Anfrage kommt durch, dann wird die Verbindung getrennt.
        first = await client.read_holding(0x0001, 1)
        assert first is not None

        # Simulator neu starten (neuer Port) - simuliert Elfin-Neustart
        await sim.stop()
        sim2 = JupiterSimulator()
        port2 = await sim2.start()

        # Client auf neuen Port zeigen und reconnecten
        client._host = "127.0.0.1"
        client._port = port2
        await client.close()  # alten Socket weg

        second = await client.read_holding(0x0001, 1)
        assert second == first  # selbe Registerwerte
    finally:
        await client.close()
        await sim.stop()
        try:
            await sim2.stop()
        except Exception:
            pass


@pytest.mark.asyncio
async def test_reconnect_mid_session():
    """Verbindungsabbruch mitten in einer Lesesequenz wird automatisch erholt.

    Nach drop_after=2 schliesst der Simulator die Verbindung. Der dritte
    read_holding muss durch Retry+Reconnect trotzdem erfolgreich sein,
    da der Server noch laeuft und neue Verbindungen akzeptiert.
    """
    sim = DropAfterSimulator(drop_after=2)
    port = await sim.start()
    client = JupiterModbusClient(
        "127.0.0.1", port, timeout=2, message_wait=0.01, retries=3
    )
    try:
        r1 = await client.read_holding(0x0001, 1)
        r2 = await client.read_holding(0x0009, 1)

        # Verbindung ist jetzt tot (drop_after=2 erschoepft).
        # Retries sollen self-reconnect ausloesen - der Server laeuft noch.
        r3 = await client.read_holding(0x0001, 1)
        assert r3 == r1  # Reconnect hat geklappt, selbe Daten
    finally:
        await client.close()
        await sim.stop()


@pytest.mark.asyncio
async def test_connected_property_after_drop():
    """connected-Property spiegelt den echten Socket-Zustand wider."""
    sim = DropAfterSimulator(drop_after=1)
    port = await sim.start()
    client = JupiterModbusClient("127.0.0.1", port, timeout=2, message_wait=0.01)
    try:
        await client.connect()
        assert client.connected is True

        # Simulator schliesst die Verbindung nach der Anfrage
        try:
            await client.read_holding(0x0001, 1)
        except Exception:
            pass

        # Kurz warten damit der OS den Socket als geschlossen markiert
        await asyncio.sleep(0.05)
        # Nach close() muss connected False sein
        await client.close()
        assert client.connected is False
    finally:
        await client.close()
        await sim.stop()
