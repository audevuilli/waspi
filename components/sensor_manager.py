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
from pySerialTransfer import pySerialTransfer as txfr


CONST_BAUD_RATE = 115200
# CONST_SERIAL_PORT = '/dev/ttyACM0'
CONST_SERIAL_PORT = txfr.GetSerialDevice()
HWID = 'SCALE'
SAMPLE_RATE = 10


def serial_rx():
    while True:
        try:
            link = txfr.SerialTransfer(
                port=CONST_SERIAL_PORT, 
                baud=CONST_BAUD_RATE, 
                restrict_ports=False
                )
            link.open()

            #while True: 
            #    link.tick()
        except Exception as e:
            print(e)

def get_value_str(link, idx, size):
    data = link.rx_obj(str, obj_byte_size=size, start_pos=idx)
    idx += size
    return (idx, data)


# Where is link defined ?? 
# where is idx defined


class WeightSensor(SensorReader):
    """A SensorReader that read load cell value every 10 seconds."""

    def __init__(self, samplerate: int, hwid: str): 
        """Initialise the weight sensing."""
        # Reading interval
        self.samplerate = SAMPLE_RATE
        self.hwid = HWID

    def get_sensor_reading(self) -> SensorValue:
        """Get sensor reading every 10 second."""
        
        with serial.Serial(CONST_SERIAL_PORT, CONST_BAUD_RATE, timeout=1) as ser:
            print("Serial connection established.")

            # Get 100 readings in 1 second
            for reading in range(100):
                arduino_data = ser.readline.decode('utf-8').strip()
                weight_data = float(round(arduino_data.split(": ")[1]),3)
                

            
            # Read data from the Arduino 
            arduino_data = ser.readline().decode('utf-8').rstrip()
            print(arduino_data)
            
        # Parse the received data (assuming data format is "Weight Scale Data: <value>")
        weight_data = float(arduino_data.split(": ")[1])
        timestamp = datetime.datetime.now()

        sensor_value = SensorValue(
            datetime=timestamp, 
            hwid=self.hwid, 
            value=weight_data, 
            deployment=None)
        print(f"Sensor Value: {weight_data}")

        return sensor_value