import datetime
import asyncio
import time

#from components.accel_logger import AccelLogger
from components.sensor_manager import SensorReporter, SerialReceiver
from components.message_factories import MessageBuilder
from components.messengers import MQTTMessenger
import config_mqtt

CONST_SERIAL_PORT = '/dev/ttyACM0'
CONST_BAUD_RATE = 115200
HWID_LIST = ["weight_scale", "temperature", "humidity"]

ADC_CHANNEL_ACCEL0 = 0
ADC_BITS = 10
ACCEL_SAMPLERATE = 16000 #16KHz
ACCEL_SAMPLEDURATION = 30 #30 seconds


"""Create the sensor object."""
ws_reporter = SensorReporter(hwid_list=HWID_LIST)

"""Create the Serial_Rx object."""
#serial_rx = SerialReceiver(port=CONST_SERIAL_PORT, baud=CONST_BAUD_RATE, hwid_list=HWID_LIST)

"""Create the Accelerometer_Logger object."""
accel_logger = AccelLogger(
    adc_channel = ADC_CHANNEL_ACCEL0,
    adc_bitdepth = ADC_BITS, 
    sampling_rate = ACCEL_SAMPLERATE,
    sampling_duration = ACCEL_SAMPLEDURATION, 
)

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
        sensors_values = await serial_rx.get_SerialRx()
        print(f"JSON MESSAGE PROCESS: {sensors_values}")
        print("")
        # Create the messages from the serial output (sensor values)
        mqtt_message = await message_factories.build_message(sensors_values)
        print(f"MQTT Message: {mqtt_message}")
        # Send sensor values to MQTT
        response = await mqtt_messenger.send_message(mqtt_message)
        print(f"MQTT Response: {response}")
        print("")

        print(f"END LOOP - TIME: {time.asctime()}")  
        print("")


#async def process_accel():
#def process_accel():
#    
#    if time.localtime().tm_min % 30 == 0:
#        accel_values = accel_logger.get_AccelData()
#        print(f"Accel Values: {accel_values}")
#        #await asyncio.get_event_loop().run_in_executor(None, accel_values)
#        # accel_values = await accel_logger.get_AccelData()


# Run asyncio event loop
loop = asyncio.get_event_loop()
loop.create_task(process_serial())

# Run asyncio event loop - Add run_in_executor for multithreading.
#loop = asyncio.get_event_loop(create_task(process_serial()))
#loop.get_event_loop().run_in_executor(None, process_accel())

try:
    loop.run_forever()
finally:
    loop.close()
