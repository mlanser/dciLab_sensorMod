import time
import pytest

from libs.sensorMod.src.sensor_SenseHat import Sensor


# =========================================================
#     G L O B A L S   &   P Y T E S T   F I X T U R E S
# =========================================================
@pytest.fixture()
def valid_attribs():
    return {
        'repeat': 1,      # Number of times to run speed test
        'holdTime': 60,   # Amount of time between tests
        'location': '- n/a -',
        'locationTZ': 'Etc/UTC',
        'tempUnit': 'C',  # Temp display unit: 'C' (Celsius), 'F' (Fahrenheit), 'K' (Kelvin)
        'enviro': True,   # Get environmental data (i.e. temperature, humidity, and pressure)
        'IMU': True,      # Get IMU (inertial measurement unit) data
    }


def _init_sensor(mocker, attribs):
    sensor = Sensor(attribs)
    mocker.patch.object(sensor._sensehat, 'get_temperature')
    mocker.patch.object(sensor._sensehat, 'get_temperature_from_humidity')
    mocker.patch.object(sensor._sensehat, 'get_humidity')
    mocker.patch.object(sensor._sensehat, 'get_pressure')
    mocker.patch.object(sensor._sensehat, 'get_orientation')
    mocker.patch.object(sensor._sensehat, 'get_compass_raw')
    mocker.patch.object(sensor._sensehat, 'get_accelerometer_raw')
    mocker.patch.object(sensor._sensehat, 'get_gyroscope_raw')
    mocker.patch.object(time, 'sleep')

    return sensor


# =========================================================
#                T E S T   F U N C T I O N S
# =========================================================
@pytest.mark.smoke
def test_get_data(mocker, valid_attribs):
    attribs = valid_attribs

    sensor = _init_sensor(mocker, attribs)

    sensor.get_data()
    sensor._sensehat.get_temperature.assert_called_once()
    sensor._sensehat.get_temperature_from_humidity.assert_called_once()
    sensor._sensehat.get_humidity.assert_called_once()
    sensor._sensehat.get_pressure.assert_called_once()
    sensor._sensehat.get_orientation.assert_called_once()
    sensor._sensehat.get_compass_raw.assert_called_once()
    sensor._sensehat.get_accelerometer_raw.assert_called_once()
    sensor._sensehat.get_gyroscope_raw.assert_called_once()
