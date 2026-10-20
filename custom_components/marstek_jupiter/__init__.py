"""Marstek Jupiter C+ ueber Modbus TCP."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import issue_registry as ir

from .const import (
    CONF_FAST_INTERVAL,
    CONF_MESSAGE_WAIT,
    CONF_SLOW_INTERVAL,
    CONF_STATUS_INTERVAL,
    CONF_TIMEOUT,
    CONF_UNIT_ID,
    DEFAULT_FAST_INTERVAL,
    DEFAULT_MESSAGE_WAIT,
    DEFAULT_PORT,
    DEFAULT_SLOW_INTERVAL,
    DEFAULT_STATIC_INTERVAL,
    DEFAULT_STATUS_INTERVAL,
    DEFAULT_TIMEOUT,
    DEFAULT_UNIT_ID,
    DOMAIN,
)
from .coordinator import JupiterCoordinator
from .errors import ErrorWatcher, issue_id
from .modbus import JupiterModbusClient
from .services import async_setup_services

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR, Platform.SENSOR]


@dataclass
class JupiterRuntime:
    coordinator: JupiterCoordinator


JupiterConfigEntry = ConfigEntry


def _option(entry: ConfigEntry, key: str, default):
    return entry.options.get(key, entry.data.get(key, default))


def _check_directory_name() -> None:
    """Warnt, wenn der Ordner nicht wie die Domain heisst.

    Home Assistant sucht die Entitaetsnamen unter
    ``component.marstek_jupiter.entity.sensor.<key>.name``. Der Teil
    ``marstek_jupiter`` kommt aus dem ORDNERNAMEN, nicht aus der
    manifest.json. Heisst der Ordner anders - etwa
    ``Marstek Jupiter C+`` nach einem Entpacken von Hand -, findet HA
    keine Uebersetzung. Die Integration laeuft dann zwar, aber jede
    Entitaet faellt auf den Geraetenamen zurueck: alle heissen
    "Marstek Jupiter C+" und bekommen IDs wie
    ``sensor.marstek_jupiter_c_15``.

    Das ist von aussen schwer zu erkennen, weil nichts kaputtgeht.
    Deshalb hier eine ausdrueckliche Warnung ins Protokoll.
    """
    directory = Path(__file__).resolve().parent.name
    if directory != DOMAIN:
        _LOGGER.warning(
            "Der Ordner dieser Integration heisst '%s', erwartet wird '%s'. "
            "Home Assistant findet die Entitaetsnamen deshalb nicht - alle "
            "Entitaeten heissen wie das Geraet und bekommen IDs mit "
            "angehaengter Nummer. Ordner nach "
            "'custom_components/%s' umbenennen und Home Assistant neu "
            "starten. Ueber HACS installiert passiert das nicht.",
            directory, DOMAIN, DOMAIN,
        )


async def async_setup_entry(hass: HomeAssistant, entry: JupiterConfigEntry) -> bool:
    _check_directory_name()

    client = JupiterModbusClient(
        host=entry.data[CONF_HOST],
        port=entry.data.get(CONF_PORT, DEFAULT_PORT),
        unit_id=entry.data.get(CONF_UNIT_ID, DEFAULT_UNIT_ID),
        timeout=_option(entry, CONF_TIMEOUT, DEFAULT_TIMEOUT),
        message_wait=_option(entry, CONF_MESSAGE_WAIT, DEFAULT_MESSAGE_WAIT),
    )

    coordinator = JupiterCoordinator(
        hass,
        client,
        config_entry=entry,
        fast_interval=_option(entry, CONF_FAST_INTERVAL, DEFAULT_FAST_INTERVAL),
        slow_interval=_option(entry, CONF_SLOW_INTERVAL, DEFAULT_SLOW_INTERVAL),
        status_interval=_option(entry, CONF_STATUS_INTERVAL, DEFAULT_STATUS_INTERVAL),
        static_interval=DEFAULT_STATIC_INTERVAL,
        entry_title=entry.title,
    )

    _remove_retired_entities(hass, entry)

    entry.runtime_data = JupiterRuntime(coordinator=coordinator)

    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception:
        await client.close()
        raise

    if not coordinator.data or not coordinator.data.registers:
        await client.close()
        raise ConfigEntryNotReady("Keine Registerwerte gelesen")

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Fehlercode -> Reparatur-Meldung und Ereignis marstek_jupiter_error
    watcher = ErrorWatcher(hass, coordinator, entry.entry_id)
    entry.async_on_unload(coordinator.async_add_listener(watcher.async_check))
    watcher.async_check()
    entry.async_on_unload(entry.add_update_listener(_async_reload))
    async_setup_services(hass)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: JupiterConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        await entry.runtime_data.coordinator.client.close()
    return unloaded


async def async_remove_entry(hass: HomeAssistant, entry: JupiterConfigEntry) -> None:
    """Integration entfernt: eine offene Fehlermeldung mitnehmen."""
    ir.async_delete_issue(hass, DOMAIN, issue_id(entry.entry_id))


async def _async_reload(hass: HomeAssistant, entry: JupiterConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


# Entitaeten, die es bis 1.0.0 gab und die entfallen sind. Ihre
# Registrierungen werden beim Start entfernt, sonst stuenden sie in der
# Geraeteansicht als "wird nicht mehr bereitgestellt" herum.
RETIRED_KEYS: tuple[str, ...] = (
    "diag_0012",
    "diag_0023",
    *(f"status_{addr:04x}" for addr in (0x1000, 0x1001, 0x1002, 0x1003, 0x1009, 0x100A)),
)


def _remove_retired_entities(hass: HomeAssistant, entry: ConfigEntry) -> None:
    registry = er.async_get(hass)
    removed = 0
    for key in RETIRED_KEYS:
        entity_id = registry.async_get_entity_id(
            "sensor", DOMAIN, f"{entry.entry_id}_{key}"
        )
        if entity_id is not None:
            registry.async_remove(entity_id)
            removed += 1
    if removed:
        _LOGGER.info("%d entfallene Entitaeten entfernt", removed)


