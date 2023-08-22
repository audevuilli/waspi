
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
adc_channel0 = 1
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

    #msg = 0b11
    #msg = ((msg << 1) + adc_channel0) << 5
    #msg = [msg, 0b00000000]
    #reply = spi.xfer2(msg)

    adc_accl0 = spi.xfer2([1, (8 + adc_channel) << 4, 0])
    data_accl0 = ((adc_accl0[1] & 3 << 8) + adc_accl0[2])
    print(f"Data Accel0: {data_accl0}")

    #adc_accl1 = spi.xfer2([1, (8 + self.adc_channel) << 4, 0])
    #data_accl1 = ((adc_accl1[1] & 3 << 8) + adc_accl1[2])
    #print(f"Data Accel1: {data_accl1}")

    # Calculate voltage form ADC value
    voltage_accl0 = (vref * data_accl0) / 1024 # 2**10 -> MCP3002 is a 10-bit ADC
    print(f"Voltage Accel0: {round(voltage_accl0, 3)}")
    #voltage_accl1 = (vref * adc_accl1) / 1024 # 2**10 -> MCP3002 is a 10-bit ADC
    #print(f"Voltage Accel1: {round(voltage_accl1, 3)}")

    return data_accl0, voltage_accl0

def record_file(sampling_rate, sampling_duration, adc_bitdepth):

    # Get the time
    time_now = datetime.datetime.now()
    file_path = f'{time_now.strftime("%Y%m%d_%H%M%S")}.wav'

    # Empty array to store the values
    accel_values = []

    # Get the start time 
    start_time = time.time()  # Get the start time

    while time.time() - start_time < sampling_duration:
        ata_accl0, _  = read_adc(adc_channel=adc_channel0, vref=vref)
        accel_values.append(data_accl0)
        #time.sleep(1/sampling_rate)

    # Create a WAV file to write the acceleromter values
    with wave.open(file_path, "wb") as accel_wavfile:
        accel_wavfile.setnchannels(1)
        accel_wavfile.setsampwidth(adc_bitdepth // 8)
        accel_wavfile.setframerate(sampling_rate)

        data_array = array.array('h', accel_values)
        #scaled_adc = int((adc_0 / 5.0) * 32767) 
        #data_array = struct.pack('<h', scaled_adc)
        accel_wavfile.writeframes(data_array.tobytes())
        accel_wavfile.close()

    #return 

record_file(sampling_rate, sampling_duration, adc_bitdepth)
spi.close()
