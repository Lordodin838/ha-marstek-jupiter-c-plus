CONNECTION_NETWORK_MAC = "mac"


class DeviceInfo(dict):
    """Ersatz fuer DeviceInfo.

    Seit HA 2026.11 ist DeviceInfo eine Dataclass; nachtraegliches
    info["feld"] = ... laeuft dort nur ueber eine Uebergangsschicht. Der
    Stub verbietet es, damit ein Rueckfall in den Tests auffaellt.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __setitem__(self, key, value):
        raise TypeError("DeviceInfo nur ueber den Konstruktor befuellen")
