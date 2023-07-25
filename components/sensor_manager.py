"""Implementation of a SensorReporter for waspi."""

import datetime
import serial
import time
import asyncio
from typing import List

#from data import Sensor, SensorValue
#from components.types import SensorReader
#from components.waspi_serial import serial_rx_time
from waspi_util import *

hwid = 'weight_scale'

#class SensorReporter(SensorReader):
class SensorReporter():
    """A SensorReporter that read sensor values every 10 seconds."""

    def __init__(self, hwid: str): 
        """Initialise the weight sensing."""
        self.hwid = hwid

    def get_blob(n):
        map = [
            # Load Cell
            {
            'hwid': f'{hwid}',
            'value': n['weight-scale'],
            },
        ]

        # Set timestamp
        timestamp_rx = arrow.utcnow().datetime.timestamp()
        for x in map:
            x['timestamp_rx'] = timestamp_rx
        return map

    def periodic_report(self):
        """Get sensor reading every 10 second."""

        data = {}
        idx = 0

        # 1/ Load Cell
        idx, data['weight-scale'] = get_float(link, idx)
        data['weight-scale'] = round(data['weight-scale'], 3)

        # 3/ Format Data - hwid, value, timestammp_rx
        blob = get_blob(data)
        print(blob)
        jblob = json.dumps(blob)
        print(jblob)

        return jblob


#sensor_value = SensorValue(datetime=timenow, hwid=self.hwid,
#                           value=loadCell_Value,deployment=None)
#print(sensor_value)