import multiprocessing
import time
import logging
from multiprocessing import Queue

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
### DEFINE RUNNING processes

def process_serial():
    while True:
        try:
            sensors_values = serial_rx.get_SerialRx()  # Assuming get_SerialRx is blocking
            logging.info(f"JSON MESSAGE PROCESS: {sensors_values}")
        except Exception as e:
            logging.info(f"Error fetching sensor values: {e}")
            continue

        # Create MQTT message and send data
        mqtt_message = sensorvalue_mfactory.build_message(sensors_values)
        logging.info(f"MQTT Message: {mqtt_message}")
        response = mqtt_messenger.send_message(mqtt_message)  
        logging.info(f"MQTT Response: {response}")

        # Store data in database
        dbstore.store_sensor_value(sensors_values)
        logging.info(f"Sensor Values saved in db.")

        mqtt_message_store = dbstore_message.store_message(mqtt_message)
        response_store = dbstore_message.store_response(response)


# Audio Microphone Process - Every 15 minutes
def process_audiomic():
    while True:
        if time.localtime().tm_min % 5 == 0:
            logging.info(f" --- START AUDIO MIC Recording: {time.asctime()}")
            audio_mic.record()
            logging.info(f" --- END AUDIO MIC Recording ----")
        time.sleep(60)
        

# Run the process_accel() synchronously every 30 minutes
def process_accel():
    while True: # Infinite loop to keep the process running  
        if time.localtime().tm_min % 2 == 0:
            logging.info(f" --- ACCEL RECORDING: {time.asctime()}"
            accel_rec.record()
            logging.info(f" --- ACCEL RECORDING STOP --- ")
        time.sleep(60)
        #return

##############################################
### MAIN SCRIPT - RUN processes

def main():

    # Create processes
    process_serial = multiprocessing.Process(target=read_serial, daemon=True)
    process_audiomic = multiprocessing.Process(target=record_audiomic, deamon=True)
    process_accel = multiprocessing.Process(target=record_accel, daemon=True)

    # Start processes
    process_serial.start()
    process_audiomic.start()
    process_accel.start()

    # Wait for serial_process to finish (optional)
    process_serial.join()
    process_audiomic.join()
    process_accel.join()


if __name__ == "__main__":
    main()
