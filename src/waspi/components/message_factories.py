"""Message factories for waspi."""
from typing import List
import json
import arrow
import asyncio

from waspi import data
from waspi.components.waspi_types import SerialOutputMessageBuilder


class MessageBuilder(SerialOutputMessageBuilder):

    """A SerialOutput MessageBuilder that builds message from serial outputs.  
    Format Result for with the following arguments:
       { 
            'timestamp_ms': recording timestamp of data receive through serial in unix ms,
            'hwid': hardware sensor id,
            'value': value of the sensors,
        }
    """
    async def build_message(self, serial_output: data.SerialOutput) -> List[data.Message]:

        """Build a message from a list of sensor values (Serial Output)."""
        print(" -- BUILD MESSAGE FUNCTION -- ")
        print(serial_output.dict())
        print("")
        print(" -- JSON DUMPS -- ")
        print(json.dumps(serial_output.dict()))
        print("")
        json_string = json.dumps(serial_output.dict())
        return data.Message(content=json_string)
