import datetime
import logging
import asyncio
import time

from waspi import data
from waspi.components.accel_logger import AccelLogger
from waspi.components.sensor_manager import SensorReporter, SerialReceiver
from waspi.components.message_factories import MessageBuilder
from waspi.components.messengers import MQTTMessenger
#from waspi.components.message_stores.sqlite import SqliteMessageStore
#from waspi.components.stores.sqlite import SqliteStore
from waspi import config_mqtt

# Setup the main logger
logging.basicConfig(
    filename="waspi.log",
    filemode="w",
    format="%(levelname)s - %(message)s",
    level=logging.INFO,
)

CONST_SERIAL_PORT = '/dev/ttyACM0'
CONST_BAUD_RATE = 115200
HWID_LIST = ["weight_scale", "temperature_0", "humidity_0", "temperature_1", "humidity_1"]

SPI_CHANNEL = 0
SPI_MAX_SPEED_HZ = 1200000
VREF = 3.3

ADC_CHANNEL_0 = 0
ADC_CHANNEL_1 = 1
ADC_BITDEPTH = 10
ACCEL_SAMPLERATE = 20000 #16KHz
ACCEL_SAMPLEDURATION = 30 #30 seconds 

"""Create the Serial_Rx object."""
serial_rx = SerialReceiver(port=CONST_SERIAL_PORT, baud=CONST_BAUD_RATE, hwid_list=HWID_LIST)

"""Create the Accelerometer objects."""
accel0_logger = AccelLogger(
    spi_channel = SPI_CHANNEL,
    spi_max_speed_hz = SPI_MAX_SPEED_HZ,
    vref = VREF,
    adc_channel = ADC_CHANNEL_0, 
    adc_bitdepth = ADC_BITDEPTH, 
    sampling_rate = ACCEL_SAMPLERATE, 
    sampling_duration = ACCEL_SAMPLEDURATION
    )

accel1_logger = AccelLogger(
    spi_channel = SPI_CHANNEL,
    spi_max_speed_hz = SPI_MAX_SPEED_HZ,
    vref = VREF,
    adc_channel = ADC_CHANNEL_1,
    adc_bitdepth = ADC_BITDEPTH,
    sampling_rate = ACCEL_SAMPLERATE, 
    sampling_duration = ACCEL_SAMPLEDURATION
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
        try:
            sensors_values = await serial_rx.get_SerialRx()
            print(f"JSON MESSAGE PROCESS: {sensors_values}")
            print("")
        except Exception as e:
            print(f"Error fetching sensor values: {e}")
            continue
        
        # Create the messages from the serial output (sensor values)
        #mqtt_message = await message_factories.build_message(sensors_values)
        #print(f"MQTT Message: {mqtt_message}")
        #print("")

        # Send sensor values to MQTT
        #response = await mqtt_messenger.send_message(mqtt_message)
        #print(f"MQTT Response: {response}")
        #print("")

        print(f"END LOOP - TIME: {time.asctime()}")  
        print("")


# Run the process_accel() synchronously every 30 minutes
# def process_accel():
#     while True: # Infinite loop to keep the process running  
#         if time.localtime().tm_min % 30 == 0:
#             print(f"Start Recording Accel 0")
#             record_accel0 = accel0_logger.record_file()
#             print(f"End Recording Accel 0: {record_accel0}")
#             print("")
#             
#             print(f"Start Recording Accel 1")
#             record_accel1 = accel1_logger.record_file()
#             print(f"End Recording Accel 1: {record_accel1}")
#             print("")


# Run asyncio main loop
loop = asyncio.get_event_loop()
loop.create_task(process_serial())

try:
    loop.run_forever()
finally:
    loop.close()
