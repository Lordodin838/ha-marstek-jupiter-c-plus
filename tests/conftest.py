"""pytest-Konfiguration und gemeinsame Fixtures."""
from __future__ import annotations

import os
import sys

# Stubs vor dem echten Paket einhaengen
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HERE, "stubs"))
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)

import pytest

from custom_components.marstek_jupiter import const
from custom_components.marstek_jupiter.coordinator import BlockState, JupiterCoordinator, JupiterData


@pytest.fixture
def fresh_coordinator():
    """Liefert einen frischen Coordinator und ein leeres JupiterData-Objekt."""
    def _make():
        coordinator = JupiterCoordinator(
            None, None, config_entry=None, fast_interval=10,
            slow_interval=60, status_interval=300, static_interval=3600,
            entry_title="Test",
        )
        data = JupiterData(blocks={b.key: BlockState() for b in const.BLOCKS})
        return coordinator, data
    return _make
