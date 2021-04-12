import time
import pprint
from faker import Faker
import argparse

# =========================================================
#                       G L O B A L S
# =========================================================
# Initiate 'Faker' and 'PrettyPrinter' :-)
pp = pprint.PrettyPrinter(indent=4)
faker = Faker()

_SENSOR_ATTRIBS_ = {
    'speedtest': {
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
    },
    'sensehat': {
        'repeat': 1,                # Number of times to run speed test
        'holdTime': 60,             # Amount of time between tests
        'location': '- n/a -',
        'locationTZ': 'Etc/UTC',
        'tempUnit': 'C',            # Temp display unit: 'C' (Celsius), 'F' (Fahrenheit), 'K' (Kelvin)
        'enviro': True,             # Get environmental data (i.e. temperature, humidity, and pressure)
        'IMU': True,                # Get IMU data (i.e. gyroscope, accelerometer, and magnetometer (compass)
    }
}


# =========================================================
#                  C L I   P A R S E R
# =========================================================
def shell():
    parser = argparse.ArgumentParser(
        description="Collect data from sensors via 'sensorMod' module",
        epilog="NOTE: Only call a module if the corresponding hardware/driver is installed"
    )
    parser.add_argument(
        '--sensor',
        action='store',
        type=str,
        required=True,
        help="Sensor module to use"
    )

    args = parser.parse_args()
    sensor = None

    if args.sensor not in _SENSOR_ATTRIBS_:
        print("ERROR: '{}' is not a valid sensor module!".format(args.sensor))
        exit(1)

    if args.sensor == 'speedtest':
        from .sensor_SpeedTest import Sensor
        sensor = Sensor(_SENSOR_ATTRIBS_[args.sensor])

    elif args.sensor == 'sensehat':
        from .sensor_SenseHat import Sensor
        sensor = Sensor(_SENSOR_ATTRIBS_[args.sensor])

    data = sensor.get_data()
    pp.pprint(data)


try:
    shell()

except KeyboardInterrupt:
    print('\nCancelling...')

except Exception as e:
    print('ERROR: {}'.format(e))
