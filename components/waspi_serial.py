"""Implementation of a SensorReader for waspi. 

WeightSensing uses the Sensor reader to read values from a load cell. 
The WeightSensing class should implement the get_reading() method
which return a sensor value based on the SensorValue dataclass. 
The SensorValue takes a datetime.datetime object, a value from type float.

The sensor reader takes arguments related to the sensor device. 
It specifies the sensor id, the unit of measurement, as well as, 
the samplerate (interval in ms for reading sensor values). 
"""

from time import sleep
import datetime
import time
import asyncio
import arrow
import json

import paho.mqtt.client as mqtt

from pySerialTransfer import pySerialTransfer as txfr
from waspi_util import *
import config_mqtt


CONST_SERIAL_PORT = '/dev/ttyACM0'
CONST_BAUD_RATE = 115200
hwid = 'weight_scale'

DEFAULT_HOST = config_mqtt.DEFAULT_HOST
DEFAULT_PORT = config_mqtt.DEFAULT_PORT
DEFAULT_MQTTCLIENT_USER = config_mqtt.DEFAULT_MQTTCLIENT_USER
DEFAULT_MQTTCLIENT_PASS = config_mqtt.DEFAULT_MQTTCLIENT_PASS
DEFAULT_CLIENTID = config_mqtt.DEFAULT_CLIENTID 
DEFAULT_TOPIC = config_mqtt.DEFAULT_TOPIC

###################################################################################################

def get_blob(n):
    map = [
        # Load Cell
        {
            'hwid': 'weight_scale',
            'value': n['weight-scale'],
        },
        # Temperature
        {
             'hwid': 'temperature-sensor',
             'value': n['temperature-sensor'],
        },
        # # Humidity
        {
             'hwid': 'humidity-sensor',
             'value': n['humidity-sensor'],
        },
    ]

    # Set timestamp
    timestamp_rx = arrow.utcnow().datetime.timestamp()
    for x in map:
        x['timestamp_rx'] = timestamp_rx
    
    return map

###################################################################################################

def periodic_report():

    data = {}
    idx = 0

    # 1/ Load Cell
    idx, data['weight-scale'] = get_float(link, idx)
    data['weight-scale'] = round(data['weight-scale'], 3)

    # 2/ Temperature & humidity - SHT31 sensor
    idx, data['temperature-sensor'] = get_float(link, idx)
    data['temperature-sensor'] = round(data['temperature-sensor'], 2)

    idx, data['humidity-sensor'] = get_float(link, idx)
    data['humidity-sensor'] = round(data['humidity-sensor'], 2)
    # idx, data['temperature-sensor-b'] = get_uint16_t(link, idx)
    # idx, data['humidity-sensor-b'] = get_uint16_t(link, idx)
    # idx, data['temperature-sensor-c'] = get_uint16_t(link, idx)
    # idx, data['humidity-sensor-c'] = get_uint16_t(link, idx)

    # 3/ Format Data - hwid, value, timestammp_rx
    blob = get_blob(data)
    jblob = json.dumps(blob)
    print(jblob)

    return jblob

###################################################################################################
    
callbacks = [None] * 256
callbacks[0]  = periodic_report

async def serial_rx_coroutine():
    while True:
        try: 
            global link
            link = txfr.SerialTransfer(CONST_SERIAL_PORT, baud=CONST_BAUD_RATE, restrict_ports=False)
            link.debug = True
            link.open()
            link.set_callbacks(callbacks)

            while True:
                link.tick()
                await asyncio.sleep(0.1)
            link.close()

        except Exception as e:
            print(e) 

###################################################################################################

async def mqtt_tx_coroutine():

    # Initialise the MQTT messenger.
    mqtt_client = mqtt.Client(DEFAULT_CLIENTID)
    mqtt_client.username_pw_set(DEFAULT_MQTTCLIENT_USER, DEFAULT_MQTTCLIENT_PASS)
    mqtt_client.connect(DEFAULT_HOST, DEFAULT_PORT)

    # Send Messages
    while True:
        try:
            print("Periodic Report - Jblob")
            serial_data = periodic_report()
            response = mqtt_client.publish(DEFAULT_TOPIC, payload=serial_data)
            response.wait_for_publish(timeout=5)
    
        except ValueError:
            status = data.ResponseStatus.ERROR
        except RuntimeError:
            status = data.ResponseStatus.FAILED
    
        received_on = datetime.datetime.now()
        print(recieved_on)
    
    await asyncio.sleep(9)


###################################################################################################

# Call the function to run 
loop = asyncio.get_event_loop()
loop = asyncio.create_task(serial_rx_coroutine())
loop = asyncio.create_task(mqtt_tx_coroutine())
loop.run_forever()
loop.close()

