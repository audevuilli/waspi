"""
    Read Analog Input on the RPi using the MCP3002 ADC Chip. 
    SparkFun Article: https://learn.sparkfun.com/tutorials/python-programming-tutorial-getting-started-with-the-raspberry-pi/experiment-3-spi-and-analog-input

"""
import datetime 
import time
import spidev 
import wave
import array

# Define the ADC (channel and bit depth) define recording sampling rate (in HZ)
spi_channel = 0
adc_bitdepth = 10
sampling_rate = 16000
sampling_duration = 30  #30 seconds
sampling_interval = 180  #30 minutes in sec. 


#class AccelLogger(ADCSampler):
class AccelLogger():
    """ Sample data from the accelerometer. 
    
        MCP3002 SPI Communication:
        1. START transmission: CS HIGH/LOW 
        2. SGL/DIFF: Select single-ended (1) or differential (0)
        3. ODD/SIGN: Select input channel
        4. MSBF: Enable LSB format first 
    """

    def __init__(self, adc_channel: int, adc_bitdepth: int, sampling_rate: int, sampling_duration: int):
        self.adc_channel = adc_channel
        self.sampling_rate = sampling_rate
        self.sampling_duration = sampling_duration
        #self.sampling_interval = sampling_interval
    
    #Define the SPI bus (0) and device (0)
    spi = spidev.SpiDev()
    spi.open(0, 0)
    
    # Configure MCP3002 Settings
    def read_adc(self):
        adc = spi.xfer2([1, (8 + self.adc_channel) << 4, 0])
        data = ((adc[1] & 3 << 8) + adc[2])
        # Calculate voltage form ADC value
        #voltage = (vref * adc) / 1024 # 2**10 -> MCP3002 is a 10-bit ADC
        return data

    def get_AccelData(self):

        # Get the time
        time_now = datetime.datetime.now()
        file_name = time_now.strftime("%Y%m%d_%H%M%S")

        # Empty array to store the values
        accel_values = []

        for _ in range(self.sample_duration):
            value = self.read_adc(self.adc_channel)
            accel_values.append(value)
                
        # Close the SPI Interface
        spi.close()
        #GPIO.cleanup()

        # Create a WAV file to write the acceleromter values
        with wave.open(file_name, "wb") as accel_wavfile:
            accel_wavfile.setnchannels(1)
            accel_wavfile.setsampwidth(self.adc_bitdepth // 8)
            accel_wavfile.setframerate(self.sampling_rate)

            data_array = array.array('h', accel_values)
            accel_wavfile.writeframes(accel_wavfile.tobytes())
            accel_wavfile.close()
        
        #time.sleep(self.sampling_interval - sampling_duration)
        # Create a Recording object and return it
        return data.Recording(
            path=Path(file_name),
            duration=self.sampling_duration,
            samplerate=self.sampling_rate,
            adc_channel=self.adc_channel,
        )


ADC_CHANNEL_ACCEL0 = 0
ADC_BITS = 10
ACCEL_SAMPLERATE = 16000 #16KHz
ACCEL_SAMPLEDURATION = 30 #30 seconds 

def main():

    """Create the Accelerometer_Logger object."""
    accel_logger = AccelLogger(adc_channel = ADC_CHANNEL_ACCEL0, adc_bitdepth = ADC_BITS, 
                               sampling_rate = ACCEL_SAMPLERATE, sampling_duration = ACCEL_SAMPLEDURATION)

    accel_values = accel_logger.get_AccelData()
    print("Value Sampled")


if __name__ == '__main__':
    main()