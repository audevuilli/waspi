"""Implementation of a SerialReader for waspi. """

from time import sleep
import arrow # manage timestamp
import json
import asyncio

from typing import Optional, List

from pySerialTransfer import pySerialTransfer as txfr
from waspi_types import SerialReader
from waspi_util import *

link = None
callbacks = [None] * 256

class Serial_Rx(SerialReader):

    def __init__(self, port: str, baud: int):
        
        self.port = port
        self.baud = baud
    
    def get_blob(n):
        map = [
            # Load Cell
            {
                'hwid': 'weight-scale',
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
        blob = self.get_blob(data)
        print(blob)
        jblob = json.dumps(blob)
        print(jblob)

        return jblob
        
    def serial_rx_coroutine(self):
            
        while True:
            try:
                global link
                link = txfr.SerialTransfer(port=self.port, baud=self.baud, restrict_ports=False)
                link.debug = True
                link.open()
                link.set_callbacks(callbacks)

                while True:
                    link.tick() #parse incoming packets
                    sleep(5)
                link.close()
    
            except Exception as e:
                print(e) 


    # def serial_rx_coroutine(self):
    #     
    #     global link
# 
    #     try: 
    #         link = txfr.SerialTransfer(port=self.port, baud=self.baud, restrict_ports=False)
    #         link.debug = True
    #         link.open()
    #         link.set_callbacks(callbacks)
    #     
    #         while True:
    #             try:
    #                 link.tick()
    #             except KeyboardInterrupt:
    #                 break
    #             except Exception as e:
    #                 print(e) 
    #         
    #             sleep(0.1)
    #     
    #     except Exception as e:
    #         print(e) 
# 
    #     return link
    # 
    # def serial_close(self):
    #     global link
    #     if link:
    #         link.close()

# class Serial_Rx(SerialReader):
# 
#     def __init__(self, port: str, baud: int):
#         
#         self.port = port
#         self.baud = baud
# 
#     def serial_rx_coroutine(self, callbacks = Optional[List]):
#     
#         while True:
#             try: 
#                 global link
#                 link = txfr.SerialTransfer(port=self.port, baud=self.baud, restrict_ports=False)
#                 link.debug = True
#                 link.open()
#                 link.set_callbacks(callbacks)
# 
#                 while True:
#                     link.tick()
#                     sleep(5)
#                 link.close()
# 
#             except Exception as e:
#                 print(e) 
