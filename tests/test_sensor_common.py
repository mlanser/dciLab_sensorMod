import os
import pytest

from libs.sensorMod.src.sensor_SpeedTest import Sensor as SnsrSpeedTest
# from libs.sensorMod.src.sensor_SenseHat import Sensor as SnsrSenseHat


# =========================================================
#     G L O B A L S   &   P Y T E S T   F I X T U R E S
# =========================================================
def _init_sensor(snsr):
    if snsr == 'speedtest':
        sensor = SnsrSpeedTest()
        assert isinstance(sensor, SnsrSpeedTest)
    # elif fmt == 'json':
    #     datastore = DBStoreJSON(flds, name, force)
    #     assert isinstance(datastore, DBStoreJSON)
    else:
        sensor = None

    return sensor


# =========================================================
#                T E S T   F U N C T I O N S
# =========================================================
@pytest.mark.smoke
@pytest.mark.parametrize("attribs", [{'one': 1}, {'two': 2}, {'three': 3}])
def test_parse_attribs(attribs):
    # TODO: need to find a good way to test many different combinations
    pass


@pytest.mark.smoke
@pytest.mark.parametrize("snsr", ['speedtest', 'sensehat', 'openweather'])
def test_properties(snsr):
    sensor = _init_sensor(snsr)
    if sensor is not None:
        assert sensor.type == snsr
