import time
from datetime import datetime
from copy import deepcopy
import http.client

import speedtest

from .sensor_base import _SensorBase

# =========================================================
#                      G L O B A L S
# =========================================================
_FIELD_MAP_ = {
    'timestamp':  'strIDX',
    'location':   'strIDX',
    'locationTZ': 'strIDX',
    'ping':       'float',
    'download':   'float',
    'upload':     'float',
}

# 'bytes_received': 72082596,
# 'bytes_sent': 32735232,
# 'client': {   'country': 'US',
#               'ip': '72.11.63.160',
#               'isp': 'NorthState',
#               'ispdlavg': '0',
#               'isprating': '3.7',
#               'ispulavg': '0',
#               'lat': '36.1053',
#               'loggedin': '0',
#               'lon': '-79.8762',
#               'rating': '0'},
# 'download': 57520174.12412543,
# 'location': '- n/a -',
# 'locationTZ': 'UTC',
# 'ping': 6.897,
# 'server': {   'cc': 'US',
#               'country': 'United States',
#               'd': 20.285158463253804,
#               'host': 'speedtest.northstate.net:8080',
#               'id': '17051',
#               'lat': '35.9557',
#               'latency': 6.897,
#               'lon': '-80.0053',
#               'name': 'High Point, NC',
#               'sponsor': 'North State Communications',
#               'url': 'http://speedtest.northstate.net:8080/upload.php'},
# 'share': None,
# 'timestamp': '2021-04-10T21:03:38.433008Z',
# 'upload': 26124728.949447703

_SENSOR_TYPE_:  str = 'speedtest'
_SENSOR_NAME_:  str = 'SpeedTest'

_MAX_REPEAT_:   int = 10
_MIN_HOLDTIME_: int = 60
_MAX_TIMEOUT_:  int = 30

_DEFAULT_SETTINGS_ = {
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
# parser.add_argument('--server', type=PARSER_TYPE_INT, action='append',
#                     help='Specify a server ID to test against. Can be '
#                          'supplied multiple times')
# parser.add_argument('--exclude', type=PARSER_TYPE_INT, action='append',
#                     help='Exclude a server from selection. Can be '
#                          'supplied multiple times')


# =========================================================
#              H E L P E R   F U N C T I O N S
# =========================================================


# =========================================================
#        M A I N   C L A S S   D E F I N I T I O N
# =========================================================
class Sensor(_SensorBase):
    def __init__(self, settings=None):
        _settings = _DEFAULT_SETTINGS_ if settings is None else {**_DEFAULT_SETTINGS_, **settings}

        super().__init__(
            sensorType=_SENSOR_TYPE_,
            name=_SENSOR_NAME_,
            description="Check current internet connection speed"
        )
        self._settings = _settings
        self._sensor = speedtest.Speedtest(
            timeout=min(_settings.get('timeout', 10), _MAX_TIMEOUT_),
            secure=_settings.get('https', False)
        )
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
            OSError: If 'speedtest' failed to run or experienced failure during test run.
        """
        # Check if we need to run this test several times.
        repeat = min(self._parse_attribs(attribs, 'repeat', self._settings['repeat']), _MAX_REPEAT_)
        holdTime = max(self._parse_attribs(attribs, 'holdTime', self._settings['holdTime']), _MIN_HOLDTIME_)

        # If we want to run test against a specific server,
        # then add server ID
        #
        #   i.e. servers = [1234]
        #
        servers = []

        # If we want to run single-threaded test, then set to '1'. Default
        # is 'None' which then will use SpeedTest.net server config.
        tmpThreads = self._parse_attribs(attribs, 'threads', self._settings['threads'])
        threads = 1 if str(tmpThreads) == '1' or tmpThreads == 'single' else None

        # We can skip 'upload' or 'download' test, but not both.
        doDownload = self._parse_attribs(attribs, 'download', self._settings['download'])
        doUpload = self._parse_attribs(attribs, 'upload', self._settings['upload'])

        if not doUpload and not doDownload:
            doDownload = True

        preAllocate = self._parse_attribs(attribs, 'preAllocate', self._settings['preAllocate'])

        # Run the test 'repeat' number of times and store results in data array.
        data = []

        while repeat > 0:
            repeat -= 1

            response = {
                'timestamp': datetime.utcnow().isoformat(),
                'location': self._parse_attribs(attribs, 'location', self._settings['location']),
                'locationTZ': self._parse_attribs(attribs, 'locationTZ', self._settings['locationTZ']),
                'ping': 0.0,
                'download': 0.0,
                'upload': 0.0
            }

            try:
                self._sensor.get_servers(servers)
                self._sensor.get_best_server()

                if doDownload:
                    self._sensor.download(threads=threads)

                if doUpload:
                    self._sensor.upload(threads=threads, pre_allocate=preAllocate)

                if self._parse_attribs(attribs, 'share', self._settings['share']):
                    self._sensor.results.share()

                response.update(self._sensor.results.dict())
                response.update([
                    ('location', self._parse_attribs(attribs, 'location', self._settings['location'])),
                    ('locationTZ', self._parse_attribs(attribs, 'locationTZ', self._settings['locationTZ']))
                ])

            except http.client.BadStatusLine as e:
                raise OSError(f"Unable to run SpeedTest!\n{e}")

            data.append(deepcopy(response))

            if repeat > 0:
                time.sleep(holdTime)

        return data
