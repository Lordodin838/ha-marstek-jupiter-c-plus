"""Pruefung: Registerkarte in sich stimmig."""
from __future__ import annotations

from custom_components.marstek_jupiter import binary_sensor as bs
from custom_components.marstek_jupiter import const
from custom_components.marstek_jupiter import sensor as sn
from simulator import REGISTERS


def test_block_sizes():
    for block in const.BLOCKS:
        assert block.count <= 8, f"Block {block.key} hat {block.count} Register (max 8)"


def test_blocks_in_valid_range():
    for block in const.BLOCKS:
        missing = [a for a in range(block.start, block.end + 1) if a not in REGISTERS]
        assert not missing, f"Block {block.key}: Adressen nicht im Simulator: {[hex(a) for a in missing]}"


def test_sensor_addresses_covered():
    for description in sn.SENSORS:
        for address in description.addresses:
            assert const.block_for_address(address) is not None, \
                f"Adresse 0x{address:04X} von {description.key} in keinem Leseblock"


def test_binary_sensor_addresses_covered():
    for description in bs.BINARY_SENSORS:
        assert const.block_for_address(description.address) is not None, \
            f"Adresse 0x{description.address:04X} von {description.key} in keinem Leseblock"


def test_entity_keys_unique():
    keys = [d.key for d in sn.SENSORS] + [d.key for d in bs.BINARY_SENSORS]
    assert len(keys) == len(set(keys)), "Entitaets-Schluessel nicht eindeutig"


def test_legacy_ids_unique():
    legacy = [
        d.legacy_unique_id
        for d in (*sn.SENSORS, *bs.BINARY_SENSORS)
        if d.legacy_unique_id
    ]
    assert len(legacy) == len(set(legacy)), "uebernommene unique_ids nicht eindeutig"
