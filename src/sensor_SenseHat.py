import time
from datetime import datetime
from copy import deepcopy

from sense_hat import SenseHat

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

_FAHRENHEIT_: str = 'F'
_KELVIN_:     str = 'K'
_CELSIUS_:    str = 'C'

_TEMP_CONVERTER_ = {
    'C2F': lambda t: ((t * 9/5) + 32),
    'F2C': lambda t: ((t - 32) * 5/9),
    'C2K': lambda t: (t + 273.15),
    'K2C': lambda t: (t - 273.15),
}

_SENSOR_TYPE_: str = 'SenseHat'

_DEFAULT_SETTINGS_ = {
    'repeat': 1,        # Number of times to run speed test
    'holdTime': 60,     # Amount of time between tests
    'tempUnit': 'C',    # Temp display unit: 'C' (Celsius), 'F' (Fahrenheit), 'K' (Kelvin)
    'enviro': True,     # Get environmental data (i.e. temperature, humidity, and pressure)
    'IMU': True,        # Get IMU (inertial measurement unit) data (i.e. gyroscope, accelerometer, and magnetometer (compass)
}


# =========================================================
#        M A I N   C L A S S   D E F I N I T I O N
# =========================================================
class Sensor(_SensorBase):
    def __init__(self, settings=None):
        _settings = _DEFAULT_SETTINGS_ if settings is None else settings

        super().__init__(_SENSOR_TYPE_)
        self._settings = _settings
        self._sensehat = SenseHat()
        self._flds = _FIELD_MAP_

    def reset(self, attribs=None):
        # There's nothing to 'reset' with this sensor as it is a web service.
        #
        # TODO: should we use this to 'reset' the object settings by
        #       setting them equal to 'attribs' values?
        #
        pass

    def get_data(self, attribs=None):
        """
        Run speed test on current internet connection to get data points for PING, UP-and DOWNLOAD speeds.

        Returns:
            Dict record with timestamp, ping time, download and upload speeds (bits/s), and more.

        Raises:
            SpeedtestException: If 'speedtest' failed to run or experienced failure during test run.
        """
        # Check if we need to run this test several times.
        repeat = self._parse_attribs(attribs, 'repeat', self._settings['repeat'])
        holdTime = self._parse_attribs(attribs, 'holdTime', self._settings['holdTime'])

        # We can skip 'enviro' or 'IMU' test, but not both.
        doEnviro = self._parse_attribs(attribs, 'enviro', self._settings['enviro'])
        doIMU = self._parse_attribs(attribs, 'IMU', self._settings['IMU'])

        if not doEnviro and not doIMU:
            doEnviro = True

        tempUnit = self._parse_attribs(attribs, 'tempUnit', self._settings['tempUnit'])

        # Run the test 'repeat' number of times and store results in data array.
        data = []

        while repeat > 0:
            repeat -= 1

            response = {
                'timestamp': datetime.utcnow().isoformat(),
                'location': self._parse_attribs(attribs, 'location', self._settings['location']),
                'locationTZ': self._parse_attribs(attribs, 'locationTZ', self._settings['locationTZ']),
                'tempDefault': None,
                'tempHumidity': None,
                'humidity': None,
                'pressure': None,
                'orientPitch': None,
                'orientRoll': None,
                'orientYaw': None,
                'compassX': None,
                'compassY': None,
                'compassZ': None,
                'accelX': None,
                'accelY': None,
                'accelZ': None,
                'gyroX': None,
                'gyroY': None,
                'gyroZ': None,
            }

            self._sensehat.clear()

            if doEnviro:
                tempDefault = self._sensehat.get_temperature()
                tempHumidity = self._sensehat.get_temperature_from_humidity()

                if tempUnit == _FAHRENHEIT_:
                    response.update([
                        ('tempDefault', _TEMP_CONVERTER_['C2F'](tempDefault)),
                        ('tempHumidity', _TEMP_CONVERTER_['C2F'](tempHumidity))
                    ])
                elif tempUnit == _KELVIN_:
                    response.update([
                        ('tempDefault', _TEMP_CONVERTER_['C2K'](tempDefault)),
                        ('tempHumidity', _TEMP_CONVERTER_['C2K'](tempHumidity))
                    ])
                else:
                    response.update([
                        ('tempDefault', tempDefault),
                        ('tempHumidity', tempHumidity)
                    ])

            response.update([
                ('humidity', self._sensehat.get_humidity()),
                ('pressure', self._sensehat.get_pressure())
            ])

            if doIMU:
                orient = self._sensehat.get_orientation()
                compass = self._sensehat.get_compass_raw()
                accel = self._sensehat.get_accelerometer_raw()
                gyro = self._sensehat.get_gyroscope_raw()

                response.update([
                    ('orientPitch', orient['pitch']),
                    ('orientRoll', orient['roll']),
                    ('orientYaw', orient['yaw']),
                    ('compassX', compass['x']),
                    ('compassY', compass['y']),
                    ('compassZ', compass['z']),
                    ('accelX', accel['x']),
                    ('accelY', accel['y']),
                    ('accelZ', accel['z']),
                    ('gyroX', gyro['x']),
                    ('gyroY', gyro['y']),
                    ('gyroZ', gyro['z']),
                ])

            data.append(deepcopy(response))

            if repeat > 0:
                time.sleep(holdTime)

        return data
