from abc import ABC, abstractmethod


# =========================================================
#        M A I N   C L A S S   D E F I N I T I O N
# =========================================================
class _SensorBase(ABC):
    def __init__(self, sensorType):
        self._type = sensorType

    def __str__(self):
        return '{}'.format(self._type)

    def __repr__(self):
        return "TYPE: '{}'".format(self._type)

    @staticmethod
    def _parse_attribs(attribs, key, default=None):
        if attribs is None:
            return default

        return attribs.get(key, default)

    @property
    def type(self):
        return self._type

    @abstractmethod
    def reset(self, attribs=None):
        pass

    @abstractmethod
    def get_data(self, attribs=None):
        pass
