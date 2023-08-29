"""
    Script to collect data from the Accelerometers 805M1. 
    Read Analog Input on the RPi using the MCP3002 ADC Chip. 
    SparkFun Article: https://learn.sparkfun.com/tutorials/python-programming-tutorial-getting-started-with-the-raspberry-pi/experiment-3-spi-and-analog-input

"""
import datetime 
import time
import spidev 
import wave
import array


# Define the SPI Communication Bus 
spi_channel = 0
spi_max_speed_hz = 1200000
vref = 3.3

# ADC (channel and bit depth) define recording sampling rate (in HZ)
adc_bitdepth = 10
sampling_rate = 20000
sampling_duration = 30  #30 seconds
sampling_number = sampling_duration * sampling_rate
#sampling_interval = 180  #30 minutes in sec. 

ADC_CHANNEL_0 = 0
ADC_CHANNEL_1 = 1

class AccelLogger():
    """ Sample data from the accelerometer. 
    
        MCP3002 SPI Communication:
        1. START transmission: CS HIGH/LOW 
        2. SGL/DIFF: Select single-ended (1) or differential (0)
        3. ODD/SIGN: Select input channel
        4. MSBF: Enable LSB format first 
    """

    def __init__(self, spi_channel: int, spi_max_speed_hz: int, vref: float, adc_channel: int, adc_bitdepth: int, sampling_rate: int, sampling_duration: int):
        self.spi_channel = spi_channel
        self.spi_max_speed_hz = spi_max_speed_hz
        self.vref = vref
        self.adc_channel = adc_channel
        self.adc_bitdepth = adc_bitdepth
        self.sampling_rate = sampling_rate
        self.sampling_duration = sampling_duration
        #self.sampling_interval = sampling_interval
    
        #Define the SPI bus (0) and device (0)
        spi = spidev.SpiDev(0, self.spi_channel)
        spi.max_speed_hz = self.spi_max_speed_hz

    
    # Configure MCP3002 Settings
    def read_adc(self):

        # Make sure ADC channel is 0 or 1
        if self.adc_channel != 0:
            self.adc_channel = 1

        msg = 0b11
        msg = ((msg << 1) + self.adc_channel) << 5
        msg = [msg, 0b00000000]
        reply = spi.xfer2(msg)

        # Construct single integer out of the reply (2 bytes)
        adc = (reply[0] << 8) + reply[1]

        # Last bit (0) is not part of ADC value, shift to remove it
        adc = adc >> 1

        # Calculate voltage form ADC value
        voltage = (self.vref * adc) / (2**self.adc_bitdepth)
        print(f"Voltage: {voltage}")

        return voltage


    def record_file(self):

        # Get the time
        time_now = datetime.datetime.now()
        file_path = f'{time_now.strftime("%Y%m%d_%H%M%S")}.wav'

        # Empty array to store the values
        accel_values = []

        # Get the number of samples to collect
        sampling_number = self.sampling_duration * self.sampling_rate

        # Get the start time 
        start_time = time.time()  # Get the start time

        while len(accel_values) < sampling_number:
            data_accl = self.read_adc()
            accel_values.append(data_accl)

        # Create a WAV file to write the acceleromter values
        with wave.open(file_name, "wb") as accel_wavfile:
            accel_wavfile.setnchannels(1)
            accel_wavfile.setsampwidth(self.adc_bitdepth // 8)
            accel_wavfile.setframerate(self.sampling_rate)

            data_array = array.array('f', accel_values)
            accel_wavfile.writeframes(accel_wavfile.tobytes())
            #accel_wavfile.close()
        
        # Create a Recording object and return it
        return data.Recording(
            path=Path(file_name),
            duration=self.sampling_duration,
            samplerate=self.sampling_rate,
            adc_channel=self.adc_channel,
        )

        # Close the SPI Interface
        spi.close()


SPI_CHANNEL = 0
SPI_MAX_SPEED_HZ = 1200000
VREF = 3.3

ADC_CHANNEL_0 = 0
ADC_CHANNEL_1 = 1
ADC_BITDEPTH = 10
ACCEL_SAMPLERATE = 20000 #16KHz
ACCEL_SAMPLEDURATION = 30 #30 seconds 


def main():

    """Create the Accelerometer_Logger object."""
    accel0_logger = AccelLogger(
        spi_channel = SPI_CHANNEL,
        spi_max_speed_hz = SPI_MAX_SPEED_HZ,
        vref = VREF,
        adc_channel = ADC_CHANNEL_0, 
        adc_bitdepth = ADC_BITDEPTH, 
        sampling_rate = ACCEL_SAMPLERATE, 
        sampling_duration = ACCEL_SAMPLEDURATION
        )
    
    accel1_logger = AccelLogger(
        spi_channel = SPI_CHANNEL,
        spi_max_speed_hz = SPI_MAX_SPEED_HZ,
        vref = VREF,
        adc_channel = ADC_CHANNEL_0, 
        adc_bitdepth = ADC_BITDEPTH, 
        sampling_rate = ACCEL_SAMPLERATE, 
        sampling_duration = ACCEL_SAMPLEDURATION
        )

    print(f"Start Recording Accel 0")
    record_accel0 = accel0_logger.record_file()
    print(f"End Recording Accel 0: {record_accel0}")
    print("")
    print(f"Start Recording Accel 1")
    record_accel1 = accel1_logger.record_file()
    print(f"End Recording Accel 1: {record_accel1}")

if __name__ == '__main__':
    main()