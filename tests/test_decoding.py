"""Pruefung: Wertwandlung."""
from __future__ import annotations

import struct

from custom_components.marstek_jupiter import const
from custom_components.marstek_jupiter.modbus import to_ascii, to_int16, to_uint32
from simulator import REGISTERS


def test_int16_positive():
    assert to_int16(162) == 162


def test_int16_negative():
    assert to_int16(65374) == -162


def test_uint32():
    assert to_uint32(0, 575) == 575


def test_mac_from_ascii():
    mac_registers = [REGISTERS[0x1100 + i] for i in range(6)]
    assert to_ascii(mac_registers) == "24215ee5674d"


def test_module_firmware():
    firmware = [REGISTERS[0x1200 + i] for i in range(6)]
    assert to_ascii(firmware) == "202512040647"


def test_error_code_1062():
    # 1062 dezimal = 0x426 - genau der Fall vom 15.09.2026
    assert const.error_text(1062).startswith("0x426 -"), const.error_text(1062)


def test_error_code_zero():
    assert const.error_text(0) == "kein Fehler"


def test_known_error_code():
    assert "Netz-Überspannung" in const.error_text(0x406), const.error_text(0x406)
