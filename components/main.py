import datetime

import config_mqtt
from sensor_manager import WeightSensor
from messengers import MQTTMessenger

HWID = 'weight_scale'

"""Initialise all the sensors."""
weight_sensor = components.WeightSensor(hwid=HWID) 
print(f"Weight data: {weight_sensor} - {time.asctime()}")

"""Initialise the MQTT Messenger."""
mqtt_messenger = components.MQTTMessenger(
        host=config_mqtt.DEFAULT_MQTT_HOST, 
        username=config_mqtt.DEFAULT_MQTT_CLIENT_USER, 
        password=config_mqtt.DEFAULT_MQTT_CLIENT_PASS, 
        port=config_mqtt.DEFAULT_MQTT_PORT, 
        clientid=config_mqtt.DEFAULT_MQTT_CLIENTID, 
        topic=config_mqtt.DEFAULT_MQTT_TOPIC
)

# Read the weight data
weight_data = weight_sensor.get_sensor_reading()
print(f"Weight data: {weight_data} - {time.asctime()}")

# Send weight data via MQTT
response = mqtt_messenger.send_message(weight_data)


def main():

    """Initialise all the sensors."""
    #weight_sensor = components.WeightSensor(hwid=HWID) 

    """Initialise the MQTT Messenger."""
    #mqtt_messenger = components.MQTTMessenger()

    def process():

        # The program start here. 
        #time_now = datetime.datetime.now()
        
        # Read sensor data
        #weight_data = weight_sensor.get_sensor_reading()

        # Send sensor data
        #mqtt_messenger.send_message()
    
    # Start processing
    #process()

#if __name__ == "__main__":
#    main()