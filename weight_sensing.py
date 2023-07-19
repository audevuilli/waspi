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
from typing import Optional, List

from data import Sensor, SensorValue
from types import SensorReader

from pySerialTransfer import pySerialTransfer as txfr

CONST_BAUD_RATE = 9600
CONST_SERIAL_PORT = '/dev/ttyACM0'
HWID = 'SCALE'

class WeightSensing(SensorReader):
    """A SensorReader that read load cell value every 10 seconds."""

    def __init__(self, samplerate: int, hwid: str): 
        """Initialise the weight sensing."""
        # Reading interval
        self.samplerate = samplerate
        self.hwid = HWID

    def read_sensor_data(self): 
        """Get sensor reading every 10 second."""
        try: 
            # Open the serial port
            ser = serial.Serial(CONST_SERIAL_PORT, CONST_BAUD_RATE, timeout=1)
            print("Serial connection established.")

            #Wait for the Arduino to initialise
            time.sleep(2)
        
            while True:
                # Read data from the Arduino 
                line = ser.readline().decode.strip()
                print(f"Arduino Line: {line}")

                try: 
                    value = float(line)
                    value_timestamp = datetime.datetime.now()

                    hwid = self.hwid

                    sensor_value = SensorValue(value_timestamp, hwid, value)

                    return sensor_value
            
                except ValueError:
                    print("Invalide data received.")

                    # Add a delay if needed
                    time.sleep(1)

        except serial.SerialException as e:
            print("Error opening the serial port:", e)

    def get_reading(self, sensor: List[str]) -> SensorValue:
        # Assuming you have multiple sensors, you can use the 'sensor' parameter
        # to identify which sensor to read from (e.g., using the sensor's ID).
        # For this example, I've hardcoded the sensor ID as 'your_sensor_hwid'.

        # Call the method to read data from the Arduino
        return self.read_sensor_data()


if __name__ == "__main__":
    reader = WeightSensing()
    reading = reader.get_reading([HWID])
    print(reading.datetime)
    print(reading.hwid)
    print(reading.value)