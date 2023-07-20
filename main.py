import datetime
import components

HWID = 'SCALE'
SAMPLE_RATE = 10

def main():

    """Initialise all the sensors."""
    weight_sensor = components.WeightSensor(
        samplerate=SAMPLE_RATE, 
        hwid=HWID
    ) 

    def process():
        # The program start here. 
        now = datetime.datetime.now()

        # Read weight sensor data
        weight_data = weight_sensor.get_sensor_reading()
        print(f"Weight Value: {weight_data} - {now}")
    
    # Start processing
    process()

if __name__ == "__main__":
    main()