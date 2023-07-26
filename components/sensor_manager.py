"""Implementation of a SensorReporter for waspi."""

import arrow
import json
from time import sleep

from pySerialTransfer import pySerialTransfer as txfr
from waspi_util import *

class SensorInfo:
    """Get Sensor Information for the given sensor HWID."""

    def __init__(self, hwid):
        self.hwid = hwid
    
    def get_SensorInfo(self, n):
        map = [
            # Set Sensor Information
            {
                'hwid': self.hwid,
                'value': n[self.hwid],  
            }
        ]
        # Set timestamp - Sensor access
        timestamp_rx = arrow.utcnow().datetime.timestamp()
        for x in map:
            x['timestamp_rx'] = timestamp_rx
        return map


class SensorReporter(SensorInfo):
    """Create the report for the given sensor HWID. -> Parent Class SensorInfo."""

    def get_PeriodicReport(self):
        
        data = {}
        idx = 0

        # 1/ Format Sensor Values
        idx, data[self.hwid] = get_float(link, idx)
        data[self.hwid] = round(data[self.hwid], 3)

        # 2/ Format Sensor Report
        sensor_info = self.get_SensorInfo(data)
        json_sensorinfo = json.dumps(sensor_info)

        return json_sensorinfo

class SerialReceiver(SensorReporter):
    """Get the sensor values from the Serial Port. -> Parent class SensorReporter, SensorInfo."""

    def __init__(self, port, baud):
        # Call the __init__ method of the parent class - SensorInfo
        super().__init__(hwid) 
        self.port = port
        self.baud = baud
  
    def get_SerialRx(self):           
        while True:
            try:
                global link
                link = txfr.SerialTransfer(self.port, self.baud, restrict_ports=False)
                link.debug = True
                link.open()

                # Set callbacks_list 
                callbacks = [self.get_PeriodicReport]
                link.set_callbacks(callbacks)

                while True:
                    link.tick() #parse incoming packets
                    sleep(5)
                link.close()
    
            except Exception as e:
                print(e) 
