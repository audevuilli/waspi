import datetime
import asyncio
import time

from components.sensor_manager import SensorReporter, SerialReceiver
from components.message_factories import MessageBuilder
from components.messengers import MQTTMessenger
import config_mqtt

# Setup the main logger
logging.basicConfig(
    filename="acoupi.log",
    filemode="w",
    format="%(levelname)s - %(message)s",
    level=logging.INFO,
)

CONST_SERIAL_PORT = '/dev/ttyACM0'
CONST_BAUD_RATE = 115200
#HWID_LIST = ["weight_scale", "temperature", "humidity"]
HWID_LIST = ["weight_scale", "temperature_0", "humidity_0", "temperature_1", "humidity_1"]

"""Create the sensor object."""
ws_reporter = SensorReporter(hwid_list=HWID_LIST)

"""Create the Serial_Rx object."""
serial_rx = SerialReceiver(port=CONST_SERIAL_PORT, baud=CONST_BAUD_RATE, hwid_list=HWID_LIST)

"""Create the message factories object."""
message_factories = MessageBuilder()

"""Initialise the MQTT Messenger."""
mqtt_messenger = MQTTMessenger(
        host=config_mqtt.DEFAULT_HOST, 
        username=config_mqtt.DEFAULT_MQTTCLIENT_USER, 
        password=config_mqtt.DEFAULT_MQTTCLIENT_PASS, 
        port=config_mqtt.DEFAULT_PORT, 
        clientid=config_mqtt.DEFAULT_CLIENTID, 
        topic=config_mqtt.DEFAULT_TOPIC
)

async def process_serial():
    while True:  # Infinite loop to keep the process running
        print(" --- START PROCESS FUNCTION --- ")
        print(f" TIME: {time.asctime()}")

        # Get the sensor values from serial port
        try:
            sensors_values = await serial_rx.get_SerialRx()
            print(f"JSON MESSAGE PROCESS: {sensors_values}")
            print("")
        except Exception as e:
            print(f"Error fetching sensor values: {e}")
            continue

        # Create the messages from the serial output (sensor values)
        mqtt_message = await message_factories.build_message(sensors_values)
        print(f"MQTT Message: {mqtt_message}")
        print("")

        # Send sensor values to MQTT
        response = await mqtt_messenger.send_message(mqtt_message)
        print(f"MQTT Response: {response}")
        print("")

        print(f"END LOOP - TIME: {time.asctime()}")
        print("")

# Run asyncio event loop
loop = asyncio.get_event_loop()
loop.create_task(process_serial())

try:
    loop.run_forever()
finally:
    loop.close()
