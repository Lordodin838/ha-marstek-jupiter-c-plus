from dataclasses import dataclass
from enum import Enum

class StrEnum(str, Enum):
    pass
from .sensor import EntityDescription

@dataclass(frozen=True, kw_only=True)
class BinarySensorEntityDescription(EntityDescription):
    device_class: object = None

class BinarySensorDeviceClass(StrEnum):
    RUNNING = "running"

class BinarySensorEntity:
    entity_id = None
    hass = None
