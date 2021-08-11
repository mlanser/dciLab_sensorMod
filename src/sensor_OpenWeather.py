import requests
import json
import time
from datetime import datetime
from copy import deepcopy

from .sensor_base import _SensorBase

# =========================================================
#                      G L O B A L S
# =========================================================
_FIELD_MAP_ = {
    'timestamp':    'strIDX',
    'location':     'strIDX',
    'locationTZ':   'strIDX',
    'tempDefault':  'float',
    'tempHumidity': 'float',
    'humidity':     'float',
    'pressure':     'float',
    'orientPitch':  'float',
    'orientRoll':   'float',
    'orientYaw':    'float',
    'compassX':     'float',
    'compassY':     'float',
    'compassZ':     'float',
    'accelX':       'float',
    'accelY':       'float',
    'accelZ':       'float',
    'gyroX':        'float',
    'gyroY':        'float',
    'gyroZ':        'float',
}

# {
#     'current': {
#         'clouds': 75,             -- Cloudiness, %
#         'dew_point': 66.33,       -- Atmospheric temp (varies based on pressure & humidity) below which water droplets begin to condense and dew can form.
#         'dt': 1626047749,         -- Current time, Unix, UTC
#         'feels_like': 86.61,      -- This temperature parameter accounts for the human perception of weather.
#         'humidity': 55,           -- Humidity, %
#         'pressure': 1016,         -- Atmospheric pressure on the sea level, hPa
#         'sunrise': 1625998270,    -- Sunrise time, Unix, UTC
#         'sunset': 1626050257,     -- Sunset time, Unix, UTC
#         'temp': 84.24,            -- Temperature. Units - default: kelvin, metric: Celsius, imperial: Fahrenheit
#         'uvi': 0.07,              -- Current UV index
#         'visibility': 10000,      -- Average visibility, metres
#         'weather': [
#             {
#                 'description': 'broken clouds',
#                 'icon': '04d',
#                 'id': 803,
#                 'main': 'Clouds'
#             }
#         ],
#         'wind_deg': 194,          -- Wind direction, degrees (meteorological)
#         'wind_speed': 9.24        -- Wind speed. Wind speed. Units – default: metre/sec, metric: metre/sec, imperial: miles/hour.
#     },
#     'lat': 36.0447,
#     'lon': -79.7662,
#     'timezone': 'America/New_York',
#     'timezone_offset': -14400
# }

_FAHRENHEIT_: str = 'F'
_KELVIN_:     str = 'K'
_CELSIUS_:    str = 'C'

_TEMP_CONVERTER_ = {
    'C2F': lambda t: ((t * 9/5) + 32),
    'F2C': lambda t: ((t - 32) * 5/9),
    'C2K': lambda t: (t + 273.15),
    'K2C': lambda t: (t - 273.15),
}

_SENSOR_TYPE_: str = 'openweather'
_SENSOR_NAME_: str = 'OpenWeather'

_MAX_REPEAT_:   int = 10
_MIN_HOLDTIME_: int = 60
_MAX_TIMEOUT_:  int = 30

_DEFAULT_SETTINGS_ = {
    'repeat': 1,                # Number of times to run speed test
    'holdTime': 60,             # Amount of time between tests
    'location': '- n/a -',
    'locationTZ': 'Etc/UTC',
    'latitude': '51.477928',
    'longitude': '-0.001545',
    'units': 'metric',
    'exclude': 'minutely,hourly,daily,alerts',
    'apiKey': '_NO_KEY_'
}


# =========================================================
#              H E L P E R   F U N C T I O N S
# =========================================================
def _clean_str(inVal):
    if inVal is None:
        return None

    tmpStr = str(inVal).strip('"')
    return tmpStr if tmpStr != '' else None


def _make_OWM_URL_params(settings) -> dict:
    return {
        'appid': settings['apiKey'],
        'lat':   settings['latitude'],
        'lon':   settings['longitude'],
        'exclude': _clean_str(settings['exclude']),
        'units': _clean_str(settings['units'])
    }


# =========================================================
#        M A I N   C L A S S   D E F I N I T I O N
# =========================================================
class Sensor(_SensorBase):
    def __init__(self, settings=None):
        _settings = _DEFAULT_SETTINGS_ if settings is None else {**_DEFAULT_SETTINGS_, **settings}

        super().__init__(
            sensorType=_SENSOR_TYPE_,
            name=_SENSOR_NAME_,
            description="Get weather and (outdoor) environmental data for current location"
        )
        self._settings = _settings
        self._url = "https://api.openweathermap.org/data/2.5/onecall"
        self._params = _make_OWM_URL_params(_settings)
        self._flds = _FIELD_MAP_

    def reset(self, attribs=None):
        # There's nothing to 'reset' with this sensor as it is a web service.
        #
        # TODO: should we use this to 'reset' the object settings by
        #       setting them equal to 'attribs' values?
        #
        pass

    def get_raw_data(self):
        """
        Get weather and environment data for current location by calling OpenWeather API.

        Returns:
            Dict record with OWM data.

        Raises:
            OSError: If OWM API call failed.
        """
        # Get JSON data from OpenWeather and convert to dict structure
        response = requests.get(self._url, params=self._params)
        data = response.json()

        if 'cod' in data:
            raise OSError(f"Unable to get data from OpenWeather!\nError: {data['cod']}")

        return data

    def get_data(self, attribs=None):
        """
        Get polished weather and environment data by parsing raw OpenWeather data.

        Returns:
            Dict record with OWM data.

        Raises:
            OSError: If OWM API call failed.
        """
        # Check if we need to run this test several times.
        repeat = min(self._parse_attribs(attribs, 'repeat', self._settings['repeat']), _MAX_REPEAT_)
        holdTime = max(self._parse_attribs(attribs, 'holdTime', self._settings['holdTime']), _MIN_HOLDTIME_)

        response = {
            'timestamp': datetime.utcnow().isoformat(),
            'location': self._parse_attribs(attribs, 'location', self._settings['location']),
            'locationTZ': self._parse_attribs(attribs, 'locationTZ', self._settings['locationTZ']),
            'clouds': 0,
            'dew_point': 0,
            'dt': 0,
            'feels_like': 0,
            'humidity': 0,
            'pressure': 0,
            'sunrise': 0,
            'sunset': 0,
            'temp': 0,
            'uvi': 0,
            'visibility': 0,
            'weather': {
                'description': 'broken clouds',
                'icon': '04d',
                'id': 803,
                'main': 'Clouds'
            },
            'wind_deg': 0,
            'wind_speed': 0
        }

        # Get OpenWeather data
        data = self.get_raw_data()

        response.update([
            ('clouds', data['current']['clouds']),
            ('dew_point', data['current']['dew_point']),
            ('dt', data['current']['dt']),
            ('feels_like', data['current']['feels_like']),
            ('humidity', data['current']['humidity']),
            ('pressure', data['current']['pressure']),
            ('sunrise', data['current']['sunrise']),
            ('sunset', data['current']['sunset']),
            ('temp', data['current']['temp']),
            ('uvi', data['current']['uvi']),
            ('visibility', data['current']['visibility']),
            ('weather', data['current']['weather'][0]),
            ('wind_deg', data['current']['wind_deg']),
            ('wind_speed', data['current']['wind_speed'])
        ])

        return response


        # {
        #     'current': {
        #         'clouds': 75,
        #         'dew_point': 66.33,
        #         'dt': 1626047749,
        #         'feels_like': 86.61,
        #         'humidity': 55,
        #         'pressure': 1016,
        #         'sunrise': 1625998270,
        #         'sunset': 1626050257,
        #         'temp': 84.24,
        #         'uvi': 0.07,
        #         'visibility': 10000,
        #         'weather': [
        #             {
        #                 'description': 'broken clouds',
        #                 'icon': '04d',
        #                 'id': 803,
        #                 'main': 'Clouds'
        #             }
        #         ],
        #         'wind_deg': 194,
        #         'wind_speed': 9.24
        #     },
        # }


