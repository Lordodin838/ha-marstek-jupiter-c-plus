from enum import Enum

class StrEnum(str, Enum):
    pass

# Testattrappe: merkt sich angelegte Meldungen in einem Dict.
ISSUES: dict[tuple[str, str], dict] = {}


class IssueSeverity(StrEnum):
    WARNING = "warning"
    ERROR = "error"


def async_create_issue(hass, domain, issue_id, **kwargs):
    ISSUES[(domain, issue_id)] = kwargs


def async_delete_issue(hass, domain, issue_id):
    ISSUES.pop((domain, issue_id), None)
