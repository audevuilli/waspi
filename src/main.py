import datetime
import logging
import asyncio
import time
from pathlib import Path

from waspi import data
from waspi.components.accel_rec import AccelRecorder
from waspi.components.audio import PyAudioRecorder
from waspi.components.sensor_manager import SensorReporter, SerialReceiver
from waspi.components.message_factories import SensorValue_MessageBuilder, AccelLogger_MessageBuilder
from waspi.components.messengers import MQTTMessenger
from waspi.components.message_stores.sqlite import SqliteMessageStore
from waspi.components.stores.sqlite import SqliteStore
from waspi import config_mqtt

# Setup the main logger
logging.basicConfig(
    filename="waspi.log",
    filemode="w",
    format="%(levelname)s - %(message)s",
    level=logging.INFO,
)

##############################################
### CONFIGURATION PARAMETERS

DEFAULT_DB_PATH = Path.home() / "storages" / "waspi.db"
DEFAULT_DB_PATH_MESSAGE = Path.home() / "storages" / "waspi_messages.db"

CONST_SERIAL_PORT = '/dev/ttyACM0'
CONST_BAUD_RATE = 115200
HWID_LIST = ["weight_scale", "temperature_0", "humidity_0", "temperature_1", "humidity_1"]

AUDIO_SAMPLERATE = 44100
AUDIO_DURATION = 15
AUDIO_CHUNKSIZE = 4096
AUDIO_CHANNEL = 1
AUDIO_DEVICE_NAME = 'WordForum USB: Audio'
AUDIO_DIR_PATH = Path.home() / "storages" / "recordings" / "audio_mic"

ACCEL_SAMPLERATE = 44100
ACCEL_DURATION = 15
ACCEL_CHANNEL = 2
#ACCEL_DEVICE_NAME = 'snd_rpi_hifiberry_dacplusadc: HiFiBerry DAC+ADC HiFi multicodec-0'
ACCEL_DIR_PATH = Path.home() / "storages" / "recordings" / "accel_rec"

###############################################
### CREATE SENSOR OBJECTS

"""Create the Serial_Rx object."""
serial_rx = SerialReceiver(port=CONST_SERIAL_PORT, baud=CONST_BAUD_RATE, hwid_list=HWID_LIST)

"""Create the Microhpone object."""
audio_mic = PyAudioRecorder(
    duration = AUDIO_DURATION,
    samplerate = AUDIO_SAMPLERATE,
    audio_channels = AUDIO_CHANNEL,
    device_name = AUDIO_DEVICE_NAME,
    chunksize = AUDIO_CHUNKSIZE,
    audio_dir = AUDIO_DIR_PATH,
    )

"""Create the Accelerometer objects."""
accel_rec = AccelRecorder(
    duration = ACCEL_DURATION,
    samplerate = ACCEL_SAMPLERATE,
    audio_channels = ACCEL_CHANNEL,
    #device_name = ACCEL_DEVICE_NAME,
    #chunksize = ACCEL_CHUNKSIZE,
    audio_dir = ACCEL_DIR_PATH,
)

"""Create the message factories object."""
sensorvalue_mfactory = SensorValue_MessageBuilder()

"""Initialise the MQTT Messenger."""
mqtt_messenger = MQTTMessenger(
    host=config_mqtt.DEFAULT_HOST, 
    username=config_mqtt.DEFAULT_MQTTCLIENT_USER, 
    password=config_mqtt.DEFAULT_MQTTCLIENT_PASS, 
    port=config_mqtt.DEFAULT_PORT, 
    clientid=config_mqtt.DEFAULT_CLIENTID, 
    topic=config_mqtt.DEFAULT_TOPIC
    )

"""Sqlite DB configuration parameters."""
dbstore = SqliteStore(db_path=DEFAULT_DB_PATH)
dbstore_message = SqliteMessageStore(db_path=DEFAULT_DB_PATH_MESSAGE)

##############################################
### DEFINE RUNNING PROCESSES

async def process_serial():
    while True:  # Infinite loop to keep the process running        
        print(" --- START PROCESS FUNCTION --- ")
        logging.info(f" --- SERIAL READ TIME: {time.asctime()}")
        
        # Get the sensor values from serial port
        try:
            sensors_values = await serial_rx.get_SerialRx()
            logging.info(f"JSON MESSAGE PROCESS: {sensors_values}")
        except Exception as e:
            logging.info(f"Error fetching sensor values: {e}")
            continue
        
        # Create the messages from the serial output (sensor values)
        mqtt_message = await sensorvalue_mfactory.build_message(sensors_values)
        logging.info(f"MQTT Message: {mqtt_message}")

        # Send sensor values to MQTT
        response = await mqtt_messenger.send_message(mqtt_message)
        logging.info(f"MQTT Response: {response}")

        # SqliteDB Store Sensor Value 
        dbstore.store_sensor_value(sensors_values)
        logging.info(f"Sensor Values saved in db.")

        # Store MQTT Message in DB
        mqtt_message_store = dbstore_message.store_message(mqtt_message)
        logging.info(f"Message store in db.")

        # Store Response in DB
        response_store = dbstore_message.store_response(response)
        logging.info(f"Reponse store in db.")
        #logging.info("")


# Audio Microphone Process - Every 15 minutes
def process_audiomic():
    while True:
        if time.localtime().tm_min % 10 == 0:
            logging.info(f" --- START AUDIO MIC Recording: {time.asctime()}")
            record_audiomic = audio_mic.record()
            logging.info(f" --- END AUDIO MIC Recording ----")
        return


# Run the process_accel() synchronously every 30 minutes
def process_accel():
    while True: # Infinite loop to keep the process running  
        if time.localtime().tm_min % 10 == 0:
            logging.info(f" --- ACCEL RECORDING: {time.asctime()}")
            record_accel = accel_rec.record()
        return

# Run asyncio main loop
async def main():
    # create the event loop
    loop = asyncio.get_event_loop()
    # Add task process_serial()
    try:
        loop.create_task(process_serial())
    except Exception as e:
        logging.info(f"Error starting process_serial: {e}")

    # Add task audio_mic
    audiomic_task = loop.run_in_executor(None, process_audiomic)
    await audiomic_task

    # Add task process_accel with run_in_exector - another thread.
    accel_task = loop.run_in_executor(None, process_accel)
    await accel_task

# Run the main loop
asyncio.run(main())
