import time
from pySerialTransfer import pySerialTransfer as txfr

CONST_BAUD_RATE = 9600
CONST_DIR_SERIAL = 'dev/serial/by-id'

CONST_DEVICE_PATH = '/dev/ttyACM0'


import argparse
parser = argparse.ArgumentParser()
parser.add_argument("device_path")
parser.add_argument("hwid")
args = parser.parse_args()

device_path = CONST_DIR_SERIAL + '/' + CONST_DEVICE_PATH
hwid = args.hwid

def get_blob(n):
	map = [
		# Humidity
		{
			'hwid': f'{hwid}S001',
			'value': n['sensor-humidity-a'],
		},
		# Temperature
		{
			'hwid': f'{hwid}S002',
			'value': n['sensor-temperature-a'],
		},
		# Water level
		{
			'hwid': f'{hwid}S003',
			'value': n['sensor-water-level'],
		},
    ]
    # Set timestamp
	when = arrow.utcnow().datetime.timestamp()
	for x in map:
		x['when'] = when

	return map