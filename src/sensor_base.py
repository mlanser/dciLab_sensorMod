from abc import ABC, abstractmethod


# =========================================================
#        M A I N   C L A S S   D E F I N I T I O N
# =========================================================
class _SensorBase(ABC):
    def __init__(self, sensorType: str, name: str, description: str = None):
        self._type = sensorType
        self._name = name
        self._desc = description

    def __str__(self):
        return f"{self._type}"

    def __repr__(self):
        return f"TYPE: '{self._type}'"

    @staticmethod
    def _parse_attribs(attribs, key, default=None):
        if attribs is None:
            return default

        return attribs.get(key, default)

    @property
    def type(self):
        return self._type

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._desc

    @abstractmethod
    def reset(self, attribs=None):
        pass

    @abstractmethod
    def get_data(self, attribs=None):
        pass
