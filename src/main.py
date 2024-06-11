import datetime
import logging
import asyncio
import time
from pathlib import Path

from waspi import data
from waspi.components.accel_logger import AccelLogger
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
AUDIO_DEVICE_NAME = 'WordForum USB: Audio (hw:2,0)'
AUDIO_DIR_PATH = Path.home() / "storages" / "recordings" / "audio_mic"

SPI_CHANNEL = 0
SPI_MAX_SPEED_HZ = 1200000
VREF = 3.3
ADC_CHANNEL_0 = 0
ADC_CHANNEL_1 = 1
ADC_BITDEPTH = 10
ACCEL_SAMPLERATE = 16000 #16KHz
ACCEL_SAMPLEDURATION = 10

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
sensorvalue_mfactory = SensorValue_MessageBuilder()
accellogger_mfactory = AccelLogger_MessageBuilder()

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
        #mqtt_message = await sensorvalue_mfactory.build_message(sensors_values)
        #logging.info(f"MQTT Message: {mqtt_message}")

        # Send sensor values to MQTT
        #response = await mqtt_messenger.send_message(mqtt_message)
        #logging.info(f"MQTT Response: {response}")

        # SqliteDB Store Sensor Value 
        dbstore.store_sensor_value(sensors_values)
        logging.info(f"Sensor Values saved in db.")

        # Store MQTT Message in DB
        #mqtt_message_store = dbstore_message.store_message(mqtt_message)
        #logging.info(f"Message store in db.")

        # Store Response in DB
        #response_store = dbstore_message.store_response(response)
        #logging.info(f"Reponse store in db.")
        #logging.info("")


# Audio Microphone Process - Every 15 minutes
def process_audiomic():
    while True:
        if time.localtime().tm_min % 1 == 0:
            logging.info(f" --- START AUDIO MIC Recording: {time.asctime()}")
            record_audiomic = audio_mic.record()

            logging.info(f" --- END AUDIO MIC Recording ----")

# Run the process_accel() synchronously every 30 minutes
def process_accel():
    while True: # Infinite loop to keep the process running  
        if time.localtime().tm_min % 2 == 0:
            logging.info(f" --- ACCEL0 START RECORDING: {time.asctime()}")
            record_accel0 = accel0_logger.record_file()

            # SqliteDB Store Accelerometer Recordings Path 
            dbstore.store_accel_recording(record_accel0)
            logging.info(f"Accel 0 Recording Path saved in db: {record_accel0}")
            logging.info("")
            
            logging.info(f" --- ACCEL1 START RECORDING: {time.asctime()}")
            record_accel1 = accel1_logger.record_file()

            # SqliteDB Store Accelerometer Recordings Path 
            dbstore.store_accel_recording(record_accel1)
            logging.info(f"Accel 1 Recording Path saved in db: {record_accel1}")
            logging.info("")

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
    #end_audiomic = await audiomic_task

    # Add task process_accel with run_in_exector - another thread. 
    #accel_task = loop.run_in_executor(None, process_accel)
    #end_accel = await accel_task

# Run the main loop
asyncio.run(main())
