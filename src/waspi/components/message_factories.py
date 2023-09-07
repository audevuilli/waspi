"""Message factories for waspi."""
from typing import List
import json
import arrow
import asyncio

from waspi import data
from waspi.components.types import SerialOutputMessageBuilder, 

class SensorValue_MessageBuilder(SerialOutputMessageBuilder):

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
        json_string = json.dumps(serial_output.dict())
        return data.Message(content=json_string)


class AccelLogger_MessageBuilder(AccelRecordingMessageBuilder):

    """A AccelLogger MessageBuilder that builds message when an accelerometer recording
    has been made. Format Result for with the following arguments:
       { 
            'datetime': recording datetime of the accelerometer,
            'hwid': hardware sensor id,
            'path': path to the recordings,
        }
    """
    #async def build_message(self, accel_logger: data.AccelRecording) -> List[data.Message]:
    def build_message(self, accel_logger: data.AccelRecording) -> List[data.Message]:

        """Build a message from a list of sensor values (Serial Output)."""
        print(accel_logger)
        print(accel_logger.dict())
        print(accel_logger.model_dump_json())
        json_string = json.dumps(accel_logger.dict())
        return data.Message(content=json_string)
