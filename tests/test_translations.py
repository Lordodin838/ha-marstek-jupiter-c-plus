"""Pruefung: jede Entitaet hat in jeder Sprache einen Namen.

Hintergrund: In 1.2.0b1 waren die beiden neuen Leistungssensoren von Hand
in translations/de.json und en.json eingetragen, fehlten aber in
build_translations.py und damit in strings.json. Der naechste Lauf des
Generators haette sie geloescht - und ohne Uebersetzungsschluessel faellt
jede Entitaet auf den Geraetenamen zurueck, inklusive durchnummerierter
Entity-IDs.

Dieser Test haelt Code und Generator zusammen: was in SENSORS oder
BINARY_SENSORS einen translation_key hat, muss in allen drei Dateien
stehen.
"""
from __future__ import annotations

import json
import os

import pytest

from custom_components.marstek_jupiter import binary_sensor as bs
from custom_components.marstek_jupiter import sensor as sn

HERE = os.path.dirname(os.path.abspath(__file__))
COMPONENT = os.path.join(
    os.path.dirname(HERE), "custom_components", "marstek_jupiter"
)
FILES = ("strings.json", "translations/en.json", "translations/de.json")


def _expected() -> dict[str, set[str]]:
    sensors = {d.translation_key for d in sn.SENSORS if d.translation_key}
    sensors |= {d.translation_key for d in sn.ENERGY_SENSORS if d.translation_key}
    # Der Klartext-Fehlersensor setzt seinen Schluessel direkt in der Klasse.
    sensors.add("error_text")
    return {
        "sensor": sensors,
        "binary_sensor": {
            d.translation_key for d in bs.BINARY_SENSORS if d.translation_key
        },
    }


@pytest.mark.parametrize("name", FILES)
def test_every_entity_has_a_name(name: str) -> None:
    with open(os.path.join(COMPONENT, name), encoding="utf-8") as handle:
        payload = json.load(handle)
    for platform, expected in _expected().items():
        present = set(payload.get("entity", {}).get(platform, {}))
        missing = sorted(expected - present)
        assert not missing, f"{name}: ohne Namen -> {missing}"


@pytest.mark.parametrize("name", FILES)
def test_no_orphaned_names(name: str) -> None:
    """Namen ohne Entitaet dahinter deuten auf eine Umbenennung hin."""
    with open(os.path.join(COMPONENT, name), encoding="utf-8") as handle:
        payload = json.load(handle)
    for platform, expected in _expected().items():
        present = set(payload.get("entity", {}).get(platform, {}))
        orphaned = sorted(present - expected)
        assert not orphaned, f"{name}: Name ohne Entitaet -> {orphaned}"
