"""Message factories for waspi."""
from typing import List
import json
import arrow
import asyncio

from components import data
from components.waspi_types import SerialOutputMessageBuilder

class MessageBuilder(SerialOutputMessageBuilder):

    """A SerialOutput MessageBuilder that builds message from serial outputs.
    
    Format Result for with the following arguments:
       { 
            'timestamp': recording timestamp of data receive through serial in unix ms,
            'hwid': hardware sensor id,
            'value': value of the sensors,
        }
    """

    async def build_message(self, serial_output: data.SerialOutput) -> List[data.Message]:

        """Build a message from a list of sensor values (Serial Output)."""

        print("")
        pritn("BUILD MESSAGE FUNCTION")
        print(f"Serial Output for json: {serial_output}")
        
        json_sensors_output = json.loads(serial_output.model_dump_json())
        print(f"JSON OUTPUT: {json_sensors_output}")

        return data.Message(content=serial_output.model_dump_json())
