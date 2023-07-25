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
import time
import asyncio
import arrow
import json

from pySerialTransfer import pySerialTransfer as txfr
from waspi_util import *


CONST_SERIAL_PORT = '/dev/ttyACM0'
CONST_BAUD_RATE = 115200
HWID = 'weight_scale'
link = None


def serial_rx():
    try: 
        link = txfr.SerialTransfer(CONST_SERIAL_PORT, baud=CONST_BAUD_RATE, restrict_ports=False)

        link.open()
        sleep(5)

        while True:
            if link.available():
                y = link.rx_obj(obj_type='f')
                print("Rx Object: {:0.3f}".format(y))

            elif link.status < 0:
                if link.status == txfer.CRC_ERROR:
                    print('ERROR: CRC_ERROR')
                elif link.status == txfer.PAYLOAD_ERROR:
                    print('ERROR: PAYLOAD_ERROR')
                elif link.status == txfer.STOP_BYTE_ERROR:
                    print('ERROR: STOP_BYTE_ERROR')
                else:
                    print('ERROR: {}'.format(link.status))

    except KeyboardInterrupt:   
        link.close()

#serial_rx_coroutine()

def get_blob(n):
    map = [
        # Load Cell
        {
            'hwid': f'{hwid}S001',
            'value': n['weight-scale'],
        },
    ]

    # Set timestamp
    when = arrow.utcnow.datetime.timestamp()
    print(f"Time now with arrow: {when}")
    time_now = datetime.datetime.now()
    print(f"Time now with datetime: {time_now}")
    for x in map:
        x['when'] = time_now
    
    return map

def periodic_report():

    data = {}
    idx = 0

    # 1/ Load Cell
    #idx, data['weight-scale'] = get_float(link, idx)
    #print(f"Weight Scale Data float: {idx, data}")
    idx, data['weight-scale'] = get_uint16_t(link, idx)
    print(f"Weight Scale Data uint16: {idx, data}")

    # 8/ Uptime
    idx, data['uptime'] = get_uint32_t(link, idx) # returns Arduino millis() ms
    data['uptime'] = data['uptime'] // 1000 # to seconds

    print(arrow.now(), data)
    print(datetime.datetime.now(), data) 
    
    blob = get_blob(data)
    jblob = json.dumps(blob)
    print(jblob)


#callbacks[0]  = periodic_report
callbacks = [None] * 256
callbacks[0]  = periodic_report
#callbacks[16]  = periodic_report

def serial_rx_time():
    while True:
        try: 
            link = txfr.SerialTransfer(CONST_SERIAL_PORT, baud=CONST_BAUD_RATE, restrict_ports=False)
            link.debug = True
            link.open()
            print(link)
            print(f"Datetime Now: {datetime.datetime.now()}")
            link.set_callbacks(callbacks)

            while True:
                link.tick()
                sleep(5)
            link.close()

        except Exception as e:
            print(e) 


serial_rx_time()