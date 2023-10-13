import datetime
import logging
import asyncio
import time

from waspi import data
from waspi.components.accel_logger import AccelLogger
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

DEFAULT_DB_PATH = "waspi_data.db"
DEFAULT_DB_PATH_MESSAGE = "waspi_message.db"

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
#ACCEL_SAMPLEDURATION = 43200 #12 hours (12*60*60) 


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
            print(f"JSON MESSAGE PROCESS: {sensors_values}")
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


# Run the process_accel() synchronously every 30 minutes
def process_accel():
    while True: # Infinite loop to keep the process running  
        if time.localtime().tm_min % 30 == 0:
            print(" --- START ACCEL FUNCTION --- ")
            logging.info(f" --- ACCEL0 START RECORDING: {time.asctime()}")
            record_accel0 = accel0_logger.record_file()

            # SqliteDB Store Accelerometer Recordings Path 
            dbstore.store_accel_recording(record_accel0)
            logging.info(f"Accel 0 Recording Path saved in db: {record_accel0}")
            logging.info("")

            # Create the messages from the accellogger
            #mqtt_message = accellogger_mfactory.build_message(record_accel0)
            #print(f"MQTT Message: {mqtt_message}")
            #print("")

            # Send accel logger to MQTT
            #response = mqtt_messenger.accellogger_send_message(mqtt_message)
            #print(f"MQTT Response: {response}")
            #print("")
            
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
    loop.create_task(process_serial())

    # Add task process_accel with run_in_exector - another thread. 
    accel_task = loop.run_in_executor(None, process_accel)
    end_accel = await accel_task

# Run the main loop
asyncio.run(main())
