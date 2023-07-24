import datetime
from sensor_manager import WeightSensor

HWID = 'weight_scale'
SAMPLE_INTERVAL = 60

def main():

    """Initialise all the sensors."""
    weight_sensor = components.WeightSensor(hwid=HWID) 

    def process():

        # The program start here. 
        time_now = datetime.datetime.now()
        print(f"Time Now: {time_now}")
        time_next_sample = time_now + datetime.timedelta(seconds=SAMPLE_INTERVAL)

        while time_now < time_next_sample:
            print(f"No Sensor Reading")
            pass

        # Read weight sensor data
        weight_data = weight_sensor.get_sensor_reading()
        print(f"Weight Value: {weight_data}")
        print(f"Time : {datetime.datetime.now()}")
        print("")
    
    # Start processing
    process()

if __name__ == "__main__":
    main()