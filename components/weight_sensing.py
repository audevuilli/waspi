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
        try: 
            # Open the serial port
            ser = serial.Serial(CONST_SERIAL_PORT, CONST_BAUD_RATE, timeout=1)
            print("Serial connection established.")

            #Wait for the Arduino to initialise
            time.sleep(2)
        
            while True:
                # Read data from the Arduino 
                line = ser.readline().decode('utf-8').rstrip()
                print(f"Arduino Line: {line}")

                try: 
                    value = float(line)
                    print(f"Value from line: {value}")
                    value_timestamp = datetime.datetime.now()

                    sensor_value = SensorValue(datetime=value_timestamp, hwid=self.hwid, value=value, deployment=None)
                    print(f"Sensor Value: {sensor_value}")

                    return sensor_value
            
                except ValueError:
                    print("Invalide data received.")

                # Add a delay between weight scale readings
                await asyncio.sleep(self.samplerate)
                    

        except serial.SerialException as e:
            print("Error opening the serial port:", e)




if __name__ == "__main__":
    reader = WeightSensing(samplerate = 10, hwid = HWID)
    reading = reader.get_reading([HWID])
    print(reading.datetime)
    print(reading.hwid)
    print(reading.value)


