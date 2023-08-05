"""Implementation of a SensorReporter for waspi."""
import arrow
import json
import asyncio
from typing import List

from pySerialTransfer import pySerialTransfer as txfr
from components import data
from components.waspi_util import *


class SensorReporter:
    """Get the sensor report for a given sensor HWID."""

    def __init__(self, hwid_list: List[str]):
        self.hwid_list = hwid_list

    def get_SensorInfo(self, n):
        """Create an sensor object."""

        sensor_values = [
            data.SensorValue(
                hwid=hwid, 
                value=n[hwid],
                timestamp=arrow.utcnow().datetime.timestamp()
            )
            for hwid in self.hwid_list
        ]

        return sensor_values

    def get_PeriodicReport(self):
        """Create a report based on the sensor object."""
        
        idx_value = {}
        idx = 0

        # 1/ Format Sensor Values
        for hwid in self.hwid_list:
            idx, idx_value[hwid] = get_float(link, idx)
            idx_value[hwid] = round(idx_value[hwid], 3)

        # 2/ Format Sensor Report
        sensor_info = self.get_SensorInfo(idx_value)
        print(sensor_info)
        print(data.SerialOutput(content=sensor_info,))

        return data.SerialOutput(content=sensor_info,)


class SerialReceiver(SensorReporter):
    """Get the sensor values from the Serial Port. -> Parent class SensorReporter."""

    def __init__(self, port, baud, hwid_list):
        # Call the __init__ method of the parent class - SensorInfo
        super().__init__(hwid_list) 
        self.port = port
        self.baud = baud

    async def get_SerialRx(self):           
        try:
            global link
            link = txfr.SerialTransfer(self.port, self.baud, restrict_ports=False)
            link.debug = True
            link.open()

            # Set callbacks_list 
            callbacks = [self.get_PeriodicReport]
            link.set_callbacks(callbacks)

            stop_event = asyncio.Event()

            async def stop_after_timeout():
                 await asyncio.sleep(10)  # Adjust the timeout value as needed
                 stop_event.set()

            asyncio.create_task(stop_after_timeout())

            while not stop_event.is_set():
                await asyncio.sleep(1)  # Give some time for callbacks to be executed
                link.tick() 

            return self.get_PeriodicReport()
         
            
        except Exception as e:
            print(e)

        link.close()