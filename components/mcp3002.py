
import time
import datetime
import spidev
import wave
import array
#import struct


# Define the SPI Communication Bus 
spi_channel = 0
spi_max_speed_hz = 1200000
vref = 3.3

# ADC (channel and bit depth) define recording sampling rate (in HZ)
adc_channel0 = 0
adc_channel1 = 1
adc_bitdepth = 10
sampling_rate = 22000
sampling_duration = 30  #30 seconds
sampling_interval = 180  #30 minutes in sec. 


spi = spidev.SpiDev()
spi.open(0, spi_channel)
spi.max_speed_hz = spi_max_speed_hz


def read_adc(adc_channel, vref):
    """ Sample data from the accelerometer. 
    
        MCP3002 SPI Communication:
        1. START transmission: CS HIGH/LOW 
        2. SGL/DIFF: Select single-ended (1) or differential (0)
        3. ODD/SIGN: Select input channel
        4. MSBF: Enable LSB format first 
    """

    msg = 0b11
    msg = ((msg << 1) + adc_channel) << 5
    msg = [msg, 0b00000000]
    reply = spi.xfer2(msg)

    # Construct single integer out of the reply (2 bytes)
    adc = (reply[0] << 8) + reply[1]

    # Last bit (0) is not part of ADC value, shift to remove it
    adc = adc >> 1

    # Calculate voltage form ADC value
    voltage = (vref * adc) / 1024

    return voltage


def record_file(sampling_rate, sampling_duration, adc_bitdepth):

    # Get the time
    time_now = datetime.datetime.now()
    file_path = f'{time_now.strftime("%Y%m%d_%H%M%S")}.wav'

    # Empty array to store the values
    accel_values = []

    # Get the start time 
    start_time = time.time()  # Get the start time

    while time.time() - start_time < sampling_duration:
        data_accl0 = read_adc(adc_channel=adc_channel0, vref=vref)
        accel_values.append(data_accl0)

    # Create a WAV file to write the acceleromter values
    with wave.open(file_path, "wb") as accel_wavfile:
        accel_wavfile.setnchannels(1)
        accel_wavfile.setsampwidth(adc_bitdepth // 8)
        accel_wavfile.setframerate(sampling_rate)

        data_array = array.array('h', accel_values)
        #scaled_adc = int((adc_0 / 5.0) * 32767) 
        #data_array = struct.pack('<h', scaled_adc)
        accel_wavfile.writeframes(data_array.tobytes())
        #accel_wavfile.close()


record_file(sampling_rate, sampling_duration, adc_bitdepth)
spi.close()
