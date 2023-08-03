import time 
import board 
import adafruit_sht4x

def read_sht45():
    
    i2c = board.I2C()
    sht = adafruit_sht4x.SHT4x(i2c)

    while True:

        try:

            temperature = sht.temperature
            humidity = sht.humidity

            print("Temperature: %0.2f" %temperature}
            print("Humidity: %0.2f" %humidity)

            time.sleep(5)
        
        except Exception as e:
            print(e)

    return

read_sht45()