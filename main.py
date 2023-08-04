import datetime
import asyncio

#from components.sensor_manager import SensorReporter, SerialReceiver
from components.sensor_manager_list import SensorReporter, SerialReceiver
from components.messengers import MQTTMessenger

import config_mqtt

CONST_SERIAL_PORT = '/dev/ttyACM0'
CONST_BAUD_RATE = 115200
#HWID = 'weight_scale'
hwid_list = ['weight_scale', 'temperature', 'humidity']

def main():
        
        """Create the sensor reporter object."""
        #ws_reporter = SensorReporter(hwid=HWID)
        ws_reporter = SensorReporter(hwid_list=hwid_list)
        
        """Create the Serial_Rx object."""
        serial_rx = SerialReceiver(port=CONST_SERIAL_PORT, baud=CONST_BAUD_RATE, hwid=hwid_list)        
        print(serial_rx)
        
        """Initialise the MQTT Messenger."""
        mqtt_messenger = MQTTMessenger(
                host=config_mqtt.DEFAULT_HOST, 
                username=config_mqtt.DEFAULT_MQTTCLIENT_USER, 
                password=config_mqtt.DEFAULT_MQTTCLIENT_PASS, 
                port=config_mqtt.DEFAULT_PORT, 
                clientid=config_mqtt.DEFAULT_CLIENTID, 
                topic=config_mqtt.DEFAULT_TOPIC
        )

        async def process():

                print(f"START PROCESS - {datetime.datetime.now()}")

                # Use asyncio.Event() to stop serial port from reading
                stop_event = asyncio.Event()

                # Create task to read data from the serial port
                serial_task = asyncio.create_task(serial_rx.get_SerialRx(stop_event))

                try: 
                        # Get the sensor values from the serial port
                        ws_values = await serial_rx.get_PeriodicReport()    
                        print(f"WS Serial Rx: {ws_values}")

                        # Send sensor values to  MQTT
                        response = await mqtt_messenger.send_message(ws_values)       
                        print(f"MQTT Response: {response}")
                
                finally:
                        # Set tue stop event to stop the serial port from reading
                        stop_event.set()

                        # Wait for serial task to complete
                        await serial_task
        
        # Start processing
        asyncio.run(process())


if __name__ == "__main__":
    main()
