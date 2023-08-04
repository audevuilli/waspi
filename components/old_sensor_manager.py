"""Implementation of a SensorReporter for waspi."""

import arrow
import json
import asyncio
from typing import List
#from time import sleep

from pySerialTransfer import pySerialTransfer as txfr
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

        #map = []
        # Set timestamp - Sensor access
        #timestamp_rx = arrow.utcnow().datetime.timestamp()

        #for hwid in self.hwid_list:
        #    map.append({
        #        'hwid' : hwid,
        #        'value': n[hwid],
        #        'timestamp_rx':timestamp_rx
        #    })
        #return map
        return sensor_values

    def get_PeriodicReport(self):
        """Create a report based on the sensor object."""
        
        data = {}
        idx = 0

        # 1/ Format Sensor Values
        for hwid in self.hwid_list:
            idx, data[hwid] = get_float(link, idx)
            data[hwid] = round(data[hwid], 3)

        # 2/ Format Sensor Report
        sensor_info = self.get_SensorInfo(data)
        json_sensorinfo = json.dumps(sensor_info)
        print(f"JSON Sensor Report: {json_sensorinfo}")
        return json_sensorinfo


class SerialReceiver(SensorReporter):
    """Get the sensor values from the Serial Port. -> Parent class SensorReporter."""

    def __init__(self, port, baud, hwid_list):
        # Call the __init__ method of the parent class - SensorInfo
        super().__init__(hwid_list) 
        self.port = port
        self.baud = baud

    async def get_SerialRx(self, stop_event):           
        try:
            global link
            link = txfr.SerialTransfer(self.port, self.baud, restrict_ports=False)
            link.debug = True
            link.open()

            # Set callbacks_list 
            callbacks = [self.get_PeriodicReport]
            print(f"CALLBACKS: {callbacks}")
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
        
        return 
  
    #def get_SerialRx(self):           
    #    while True:
    #        try:
    #            global link
    #            link = txfr.SerialTransfer(self.port, self.baud, restrict_ports=False)
    #            link.debug = True
    #            link.open()
#
    #            # Set callbacks_list 
    #            callbacks = [self.get_PeriodicReport]
    #            print(f"CALLBACKS: {callbacks}")
    #            link.set_callbacks(callbacks)
#
    #            while not stop_event.is_set():
    #                link.tick() #parse incoming packets
    #                sleep(5)
    #            link.close()
#
    #        except Exception as e:
    #            print(e)
    #            break # Exit the loop if there's an exception
    #    
    #    return 
