import datetime

import config_mqtt
from serial_reader import Serial_Rx
from sensor_manager import SensorReporter
from messengers import MQTTMessenger

#from components.serial_reader import Serial_Rx
#from components.sensor_manager import SensorReporter
#from components.messengers import MQTTMessenger


CONST_SERIAL_PORT = '/dev/ttyACM0'
CONST_BAUD_RATE = 115200
HWID = 'weight_scale'


"""Define the Serial_Rx object."""
#serial_rx = compoments.Serial_Rx(port=CONST_SERIAL_PORT, baud=CONST_BAUD_RATE)
serial_rx = Serial_Rx(port=CONST_SERIAL_PORT, baud=CONST_BAUD_RATE)

"""Define the Sensor Reporter objebt"""
#reporter = components.SensorReporter(hwid=HWID)
reporter = SensorReporter(hwid=HWID)

"""Initialise the MQTT Messenger."""
#mqtt_messenger = components.MQTTMessenger(
mqtt_messenger = MQTTMessenger(
        host=config_mqtt.DEFAULT_MQTT_HOST, 
        username=config_mqtt.DEFAULT_MQTT_CLIENT_USER, 
        password=config_mqtt.DEFAULT_MQTT_CLIENT_PASS, 
        port=config_mqtt.DEFAULT_MQTT_PORT, 
        clientid=config_mqtt.DEFAULT_MQTT_CLIENTID, 
        topic=config_mqtt.DEFAULT_MQTT_TOPIC
)

# Define the callbacks
callbacks[0] = reporter.periodic_report()

# Receive the sensor data
getSensors_value = serial_rx.serial_rx_coroutine(callbacks)
print(f"Sensor Values: {getSensors_value}")

# Send weight data via MQTT
response = mqtt_messenger.send_message(getSensors_value)
print(f"MQTT Response: {response}")



def main(): 
    """Define the Serial_Rx object."""
    """Define the Sensor Reporter objebt"""
    """Initialise the MQTT Messenger."""
   
    def process():

        # Step 1 - Define callbacks
        # Step 2 - Get Report - Sensor Values
        # Step 3 - Send sensor data
    
    # Start processing
    #process()

#if __name__ == "__main__":
#    main()