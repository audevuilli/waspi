import datetime
import logging
import asyncio
from pathlib import Path

from waspi.components.accel_rec import AccelRecorder
from waspi.components.audio import PyAudioRecorder
from waspi.components.sensor_manager import SerialReceiver
from waspi.components.message_factories import SensorValue_MessageBuilder
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
HWID_LIST = ["weight_scale", "temp_sht45_0", "hum_sht45_0", "temp_sht45_1", "hum_sht45_1"]
HWID_LIST = ["weight_scale", "temp_sht45_0", "hum_sht45_0", "temp_sht45_1", "hum_sht45_1", "temp_scd41", "hum_scd41", "co2ppm_scd41"]

AUDIO_SAMPLERATE = 44100
AUDIO_DURATION = 15
AUDIO_CHUNKSIZE = 4096
AUDIO_CHANNEL = 1
AUDIO_DEVICE_NAME = 'WordForum USB: Audio'
AUDIO_DIR_PATH = Path.home() / "storages" / "recordings" / "audio_mic"

ACCEL_SAMPLERATE = 44100
ACCEL_DURATION = 15
ACCEL_CHANNEL = 2
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
        logging.info(f" --- SERIAL READ START: {datetime.datetime.now()}")
        
        # Get the sensor values from serial port
        try:
            sensors_values = await serial_rx.get_SerialRx()
            print(f"Sensor Values: {sensors_values}")
            logging.info(f"JSON MESSAGE PROCESS: {sensors_values}")
        except Exception as e:
            logging.info(f"Error fetching sensor values: {e}")
            continue
            # Create the messages from the serial output (sensor values)
   
        mqtt_message = await sensorvalue_mfactory.build_message(sensors_values)
        # Send sensor values to MQTT
        response = await mqtt_messenger.send_message(mqtt_message)
        # SqliteDB Store Sensor Value
        dbstore.store_sensor_value(sensors_values)
        # Store MQTT Message in DB
        mqtt_message_store = dbstore_message.store_message(mqtt_message)
        # Store Response in DB
        response_store = dbstore_message.store_response(response)
        logging.info(" --- END SERIAL ---")

# Audio Microphone Process - Every 10 minutes
async def process_audio():
    while True:
        logging.info(f" --- START AUDIO RECORDING {datetime.datetime.now()} --- ")
        audio_mic.record()
        accel_rec.record()
        logging.info(f" --- END AUDIO RECORDING {datetime.datetime.now()} ----")
        await asyncio.sleep(600 - AUDIO_DURATION)


async def main():
    """ Run the main loop.
    1. Run the process_serial().
    2. Run the process_audio() - Record audio and accel for 15 seconds every 10 minutes.
    """

    loop = asyncio.get_event_loop()
    serial_task = loop.create_task(process_serial())
    audio_task = loop.create_task(process_audio())

    await asyncio.gather(serial_task, audio_task)

asyncio.run(main())
