"""Implementation of a SensorReader for waspi. 

WeightSensing uses the Sensor reader to read values from a load cell. 
The WeightSensing class should implement the get_reading() method
which return a sensor value based on the SensorValue dataclass. 
The SensorValue takes a datetime.datetime object, a value from type float.

The sensor reader takes arguments related to the sensor device. 
It specifies the sensor id, the unit of measurement, as well as, 
the samplerate (interval in ms for reading sensor values). 
"""

from time import sleep
import datetime
import time
import asyncio
import arrow
import json

from pySerialTransfer import pySerialTransfer as txfr
from waspi_util import *


CONST_SERIAL_PORT = '/dev/ttyACM0'
CONST_BAUD_RATE = 115200
hwid = 'weight_scale'

def get_blob(n):
    map = [
        # Load Cell
        {
            'hwid': 'weight_scale',
            'value': n['weight-scale'],
        },
        # Temperature
        {
             'hwid': 'sensor-temperature',
             'value': n['sensor-temperature'],
        },
        # # Humidity
        {
             'hwid': 'sensor-humidity',
             'value': n['sensor-humidity'],
        },
    ]

    # Set timestamp
    timestamp_rx = arrow.utcnow().datetime.timestamp()
    for x in map:
        x['timestamp_rx'] = timestamp_rx
    
    return map


def periodic_report():

    data = {}
    idx = 0

    # 1/ Load Cell
    idx, data['weight-scale'] = get_float(link, idx)
    data['weight-scale'] = round(data['weight-scale'], 3)

    # 2/ Temperature & humidity - SHT31 sensor
    idx, data['temperature-sensor'] = get_float(link, idx)
    idx, data['humidity-sensor'] = get_float(link, idx)
    # idx, data['temperature-sensor-b'] = get_uint16_t(link, idx)
    # idx, data['humidity-sensor-b'] = get_uint16_t(link, idx)
    # idx, data['temperature-sensor-c'] = get_uint16_t(link, idx)
    # idx, data['humidity-sensor-c'] = get_uint16_t(link, idx)

    # 3/ Format Data - hwid, value, timestammp_rx
    blob = get_blob(data)
    jblob = json.dumps(blob)
    print(jblob)

    return jblob


callbacks = [None] * 256
callbacks[0]  = periodic_report

async def serial_rx_coroutine():
    while True:
        try: 
            global link
            link = txfr.SerialTransfer(CONST_SERIAL_PORT, baud=CONST_BAUD_RATE, restrict_ports=False)
            link.debug = True
            link.open()
            link.set_callbacks(callbacks)
            print(f"after link.set_callbacks: {link}")

            while True:
                link.tick()
                await asyncio.sleep(0.1)
            link.close()

        except Exception as e:
            print(e) 

serial_rx_coroutine()

#loop = asyncio.create_task(serial_rx_coroutine())
#loop = asyncio.get_event_loop()
#loop.close()

