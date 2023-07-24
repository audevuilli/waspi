"""Implementation of a SensorReader for waspi. 

WeightSensing uses the Sensor reader to read values from a load cell. 
The WeightSensing class should implement the get_reading() method
which return a sensor value based on the SensorValue dataclass. 
The SensorValue takes a datetime.datetime object, a value from type float.

The sensor reader takes arguments related to the sensor device. 
It specifies the sensor id, the unit of measurement, as well as, 
the samplerate (interval in ms for reading sensor values). 
"""

import datetime
import serial
import time
import asyncio
from typing import List

#from data import Sensor, SensorValue
#from components.types import SensorReader
from pySerialTransfer import pySerialTransfer as txfr


CONST_SERIAL_PORT = '/dev/ttyACM0'

CONST_BAUD_RATE = 115200
HWID = 'SCALE'
link = None

def serial_rx():
    try: 
        link = txfr.SerialTransfer(CONST_SERIAL_PORT, baud=CONST_BAUD_RATE, restrict_ports=False)

        link.open()
        sleep(5)
    
        while True:
            if link.available():
                y = link.rx_obj(obj_type='f')
                print(f"Rx Object: {y}")

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

serial_rx()