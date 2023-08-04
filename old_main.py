import datetime
import asyncio

from components.old_sensor_manager import SensorReporter, SerialReceiver
from components.message_factories import MessageBuilder
from components.messengers import MQTTMessenger
import config_mqtt

CONST_SERIAL_PORT = '/dev/ttyACM0'
CONST_BAUD_RATE = 115200
#HWID = 'weight_scale'
HWID_LIST = ["weight_scale", "temperature", "humidity"]

def main():

        """Create the sensor object."""
        ws_reporter = SensorReporter(hwid_list=HWID_LIST)

        """Create the Serial_Rx object."""
        serial_rx = SerialReceiver(port=CONST_SERIAL_PORT, baud=CONST_BAUD_RATE, hwid_list=HWID_LIST)

        """Create the message factories object."""
        message_factories = [MessageBuilder()]

        """Initialise the MQTT Messenger."""
        mqtt_messenger = MQTTMessenger(
                host=config_mqtt.DEFAULT_HOST, 
                username=config_mqtt.DEFAULT_MQTTCLIENT_USER, 
                password=config_mqtt.DEFAULT_MQTTCLIENT_PASS, 
                port=config_mqtt.DEFAULT_PORT, 
                clientid=config_mqtt.DEFAULT_CLIENTID, 
                topic=config_mqtt.DEFAULT_TOPIC
        )
        async def process():
                
                print(" --- START PROCESS FUNCTION --- ")

                # Get the sensor values from serial port
                serial_output = await serial_rx.get_SerialRx()
                print(f"JSON MESSAGE PROCESS: {serial_output}")

                # Create the messages from the serial output (sensor values)
                #mqtt_messages = [message_factory.build_message(serial_output) for message_factory in message_factories]
                mqtt_message = await message_factories.build_message(serial_output)
                print(f"MQTT Message: {mqtt_message}")

                # Send sensor values to  MQTT
                response = await mqtt_messenger.send_message(mqtt_message)       
                print(f"MQTT Response: {response}")
        
        # Start processing
        asyncio.run(process())

if __name__ == "__main__":
    main()