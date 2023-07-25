"""Implementation of a SerialReader for waspi. 

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
from typing import Optional, List

from pySerialTransfer import pySerialTransfer as txfr
from components.waspi_types import SerialReader
from waspi_util import *

link = None
callbacks = [None] * 256

class Serial_Rx(SerialReader):

    def __init__(self, port: str, baud: int):
        
        self.port = port
        self.baud = baud

    def serial_rx_coroutine(self, callbacks = Optional[List]):
    
        while True:
            try: 
                global link
                link = txfr.SerialTransfer(port=self.port, baud=self.baud, restrict_ports=False)
                link.debug = True
                link.open()
                link.set_callbacks(callbacks)

                while True:
                    link.tick()
                    sleep(5)
                link.close()

            except Exception as e:
                print(e) 
