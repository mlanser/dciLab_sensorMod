import time
import pytest

from libs.sensorMod.src.sensor_SpeedTest import Sensor


# =========================================================
#     G L O B A L S   &   P Y T E S T   F I X T U R E S
# =========================================================
@pytest.fixture()
def valid_attribs():
    return {
        'repeat': 1,                # Number of times to run speed test
        'holdTime': 60,             # Amount of time between tests
        'servers': [],
        'threads': 'multi',         # 'single' | 'multi' -- use 1 (single) or multiple threads
        'unit': 'bits',             # 'bits' | 'bytes' -- show values in 'bits' or 'bytes' (1 byte = 8 bits)
        'share': False,             # Share results with speedtest.net
        'location': '- n/a -',
        'locationTZ': 'Etc/UTC',
        'host': None,
        'https': False,             # Use secure 'https' connection
        'timeout': 10,              # HTTP timeout in seconds
        'preAllocate': True,        # Pre-allocation is enabled by default to improve upload performance.
        'upload': True,             # Perform upload test
        'download': True,           # Perform download test
    }


def _init_sensor(mocker, attribs):
    sensor = Sensor(attribs)
    mocker.patch.object(sensor._speedtest, 'get_servers')
    mocker.patch.object(sensor._speedtest, 'get_best_server')
    mocker.patch.object(sensor._speedtest, 'download')
    mocker.patch.object(sensor._speedtest, 'upload')
    mocker.patch.object(sensor._speedtest.results, 'share')
    mocker.patch.object(sensor._speedtest.results, 'dict')
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
    sensor._speedtest.get_servers.assert_called_once()
    sensor._speedtest.get_best_server.assert_called_once()
    sensor._speedtest.download.assert_called_once()
    sensor._speedtest.upload.assert_called_once()


@pytest.mark.smoke
def test_get_data_loop(mocker, valid_attribs):
    mocker.patch.object(time, 'sleep')

    attribs = valid_attribs
    attribs['repeat'] = 2
    attribs['holdTime'] = 60

    sensor = _init_sensor(mocker, attribs)
    sensor.get_data()
    time.sleep.assert_called_once_with(attribs['holdTime'])


def test_reset(mocker):
    # mocker.patch('os.get_terminal_size', return_value=(80, 80))
    #
    # display = Display()
    # mocker.patch.object(display._console, 'log')
    #
    # data = ['apple', 'banana', 'orange']
    # display.display_log(data)
    # display._console.log.assert_called_once_with(data)
    pass
