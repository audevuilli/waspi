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
#CONST_SERIAL_PORT = txfr.GetSerialDevice()
#print("Serial Port: {CONST_SERIAL_PORT}")
CONST_BAUD_RATE = 115200

HWID = 'SCALE'
SAMPLE_RATE = 10
start_pos = 0

link = txfr.SerialTransfer(
    port=CONST_SERIAL_PORT,
    baud=CONST_BAUD_RATE,
    restrict_ports=False,
    timeout=0.5)

link = serial.Serial(port=CONST_SERIAL_PORT, baud=CONST_BAUD_RATE, timeout=0.5)
link.close()
link.open()

input_buffer = link.read_all()
print(input_buffer)

# Request to arduino code
link.write(bytes([start_pos]))
message = link.read_until()
decode_message = message.decode()
print(f"Message: {decode_message}")

