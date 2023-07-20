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

CONST_BAUD_RATE = 9600
CONST_SERIAL_PORT = '/dev/ttyACM0'
HWID = 'SCALE'
SAMPLE_RATE = 10

class WeightSensor(SensorReader):
    """A SensorReader that read load cell value every 10 seconds."""

    def __init__(self, samplerate: int, hwid: str): 
        """Initialise the weight sensing."""
        # Reading interval
        self.samplerate = SAMPLE_RATE
        self.hwid = HWID

    def get_sensor_reading(self, sensor: List[Sensor]) -> SensorValue:
        """Get sensor reading every 10 second."""
        
        with serial.Serial(CONST_SERIAL_PORT, CONST_BAUD_RATE, timeout=1) as ser:
            print("Serial connection established.")
            
            # Read data from the Arduino 
            arduino_data = ser.readline().decode('utf-8').rstrip()
            
        # Parse the received data (assuming data format is "Weight Scale Data: <value>")
        weight_data = float(arduino_data.split(": ")[1])
        timestamp = datetime.datetime.now()

        sensor_value = SensorValue(
            datetime=value_timestamp, 
            hwid=self.hwid, 
            value=weight_data, 
            deployment=None)
        print(f"Sensor Value: {weight_data}")

        return sensor_value