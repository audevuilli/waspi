import datetime
import config_mqtt
from sensor_manager import SensorInfo, SensorReporter, SerialReceiver
from messengers import MQTTMessenger

#from components.serial_reader import Serial_Rx
#from components.sensor_manager import SensorReporter
#from components.messengers import MQTTMessenger


CONST_SERIAL_PORT = '/dev/ttyACM0'
CONST_BAUD_RATE = 115200
HWID = 'weight_scale'

"""Define the Sensor object."""

hwid_ws = SensorInfo('weight_scale')
ws_report = SensorReporter(hwid_ws) 
print("")
print(f"WS Reporter: {ws_report}")

"""Define the Serial_Rx object."""
serial_rx = SerialReceiver(port=CONST_SERIAL_PORT, baud=CONST_BAUD_RATE)
print("")
print(f"WS Serial Rx: {serial_rx}")

ws_values = serial_rx.get_SerialRx()
print("")
print(f"WS Serial Rx: {ws_values}")



#serial_rx = compoments.Serial_Rx(port=CONST_SERIAL_PORT, baud=CONST_BAUD_RATE)
#serial_rx = Serial_Rx(port=CONST_SERIAL_PORT, baud=CONST_BAUD_RATE)

"""Initialise the MQTT Messenger."""
#mqtt_messenger = components.MQTTMessenger(
mqtt_messenger = MQTTMessenger(
        host=config_mqtt.DEFAULT_HOST, 
        username=config_mqtt.DEFAULT_MQTTCLIENT_USER, 
        password=config_mqtt.DEFAULT_MQTTCLIENT_PASS, 
        port=config_mqtt.DEFAULT_PORT, 
        clientid=config_mqtt.DEFAULT_CLIENTID, 
        topic=config_mqtt.DEFAULT_TOPIC
)

# Send weight data via MQTT
response = mqtt_messenger.send_message(ws_values)
print(f"MQTT Response: {response}")
