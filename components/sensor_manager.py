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

from data import Sensor, SensorValue
from components.types import SensorReader
from components.waspi_serial import serial_rx_coroutine

CONST_BAUD_RATE = 115200
CONST_SERIAL_PORT = '/dev/ttyACM0'
HWID = 'weight_scale'
SAMPLE_COUNT = 10

class WeightSensor(SensorReader):
    """A SensorReader that read load cell value every 10 seconds."""

    def __init__(self, hwid: str): 
        """Initialise the weight sensing."""
        self.hwid = HWID

    def get_sensor_reading(self) -> SensorValue:
        """Get sensor reading every 10 second."""

        # Get the start time 
        timenow = datetime.datetime.now()
        print(f"Time now is: {time}")
        
        # Create an arra to receive the data from the sensor
        loadCell_Buffer = []
        
        for i in range(0, SAMPLE_COUNT):
            data = serial_rx_coroutine()
            loadCell_Buffer.append(data)
        
        # Calculate the average value over 1 second
        loadCell_Value = float(sum(loadCell_Buffer)/len(loadCell_Buffer))
        print(f"Load Cell Value is: {loadCell_Value}")

        sensor_value = SensorValue(
            datetime=timenow, 
            hwid=self.hwid,
            value=loadCell_Value, 
            deployment=None
        )

        return sensor_value