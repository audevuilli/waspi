"""Implementation of a SensorReporter for waspi."""

import arrow
import json
from time import sleep
import asyncio
from typing import List

#from data import Sensor, SensorValue
#from components.types import SensorReader
#from components.waspi_serial import serial_rx_time
from waspi_util import *

hwid = 'weight_scale'


class SensorInfo:

    def __init__(self, hwid):
        self.hwid = hwid
    
    @staticmethod
    def get_SensorInfo(hwid):
        map = [
            # Set Sensor Information
            {
                'hwid': f'{self.hwid}',
                'value': n[f'{self.hwid}'],  
            }
        ]
        # Set timestamp - Sensor access
        timestamp_rx = arrow.utcnow().datetime.timestamp()
        for x in map:
            x['timestamp_rx'] = timestamp_rx
        return map

class SensorReporter(SensorInfo):

    @staticmethod
    def get_PeriodicReport(self):
        
        data = {}
        idx = 0

        # 1/ Format Sensor Values
        idx, data[str(self.hwid)] = get_float(link, idx)
        data[str(self.hwid)] = round(data[str(self.hwid)], 3)

        # 2/ Format Sensor Report
        sensor_info = SensorInfo.get_SensorInfo(data)
        print(f"SENSOR INFO: {sensor_info}")
        json_sensorinfo = json.dumps(sensor_info)

        return json_sensorinfo

class SerialReceiver(SensorReporter):

    def __init__(self, port, baud):
        self.port = port
        self.baud = baud
    
    @staticmethod
    def get_SerialRx(self):           
        while True:
            try:
                global link
                link = txfr.SerialTransfer(port=self.port, baud=self.baud, restrict_ports=False)
                link.debug = True
                link.open()

                # Set callbacks_list 
                callbacks_list = [SensorReporter.get_PeriodicReport]
                link.set_callbacks(callbacks_list)

                while True:
                    link.tick() #parse incoming packets
                    sleep(5)
                link.close()
    
            except Exception as e:
                print(e) 
