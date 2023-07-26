import datetime
import config_mqtt
from components.sensor_manager import SensorReporter, SerialReceiver
from components.messengers import MQTTMessenger

from config_mqtt import *

CONST_SERIAL_PORT = '/dev/ttyACM0'
CONST_BAUD_RATE = 115200
HWID = 'weight_scale'


def main():
        
        """Create the sensor object."""
        #hwid_ws = SensorInfo(hwid=HWID)  
        hwid_ws = SensorReporter(hwid=HWID)
        
        """Create the sensor reporter object."""
        #ws_report = SensorReporter(hwid_ws)     
        
        """Create the Serial_Rx object."""
        serial_rx = SerialReceiver(port=CONST_SERIAL_PORT, baud=CONST_BAUD_RATE)        
        
        """Initialise the MQTT Messenger."""
        mqtt_messenger = MQTTMessenger(
                host=config_mqtt.DEFAULT_HOST, 
                username=config_mqtt.DEFAULT_MQTTCLIENT_USER, 
                password=config_mqtt.DEFAULT_MQTTCLIENT_PASS, 
                port=config_mqtt.DEFAULT_PORT, 
                clientid=config_mqtt.DEFAULT_CLIENTID, 
                topic=config_mqtt.DEFAULT_TOPIC
        )

        def process():

                # Get the sensor values from serial port
                ws_values = serial_rx.get_SerialRx()
                print("")
                print(f"WS Serial Rx: {ws_values}")

                # Send sensor values to  MQTT
                response = mqtt_messenger.send_message(ws_values)       
                print(f"MQTT Response: {response}")
        
        # Start processing
        process()


if __name__ == "__main__":
    main()