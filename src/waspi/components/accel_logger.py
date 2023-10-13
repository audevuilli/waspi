"""
    Collect data from the Accelerometers 805M1. Use the MCP3002 ADC Chip.
    SparkFun Article: https://learn.sparkfun.com/tutorials/python-programming-tutorial-getting-started-with-the-raspberry-pi/experiment-3-spi-and-analog-input

"""
import datetime
import time
import spidev
import wave
import array
import asyncio

from pathlib import Path

from waspi import data



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
        self.sampling_rate = sampling_rate  #8000 Hz - maximum of 8000Hz 
        self.sampling_duration = sampling_duration
        #self.sampling_interval = sampling_interval

    def read_adc(self, spi):

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

        return voltage


    def record_file(self):

        #Define the SPI bus (0) and device (0)
        spi = spidev.SpiDev(0, self.spi_channel)
        spi.max_speed_hz = self.spi_max_speed_hz

        output_folder = 'recordings/accelRecordings/'

        # Create the file path usint the start time. 
        recording_starttime = datetime.datetime.now()
        file_path = f'{recording_starttime.strftime("%Y%m%d_%H%M%S")}.wav'
        hwid_accel = "accel"+str(self.adc_channel)
        final_file_path = output_folder + hwid_accel + "_" + file_path 

        # Empty array to store the values
        accel_values = []

        # Get the start time 
        start_time = time.time()  # Get the start time

        #while time.time() - start_time < (self.sampling_duration * self.sampling_rate):
        while time.time() - start_time < self.sampling_duration:
            data_accl = self.read_adc(spi)
            accel_values.append(data_accl)

        # for _ in range(self.sampling_duration * self.sampling_rate):
        #   data_accl = self.read_adc(spi)
        #   accel_values.append(data_accl)

        # Create a WAV file to write the acceleromter values
        with wave.open(final_file_path, "wb") as accel_wavfile:
            accel_wavfile.setnchannels(1)
            accel_wavfile.setsampwidth(self.adc_bitdepth // 8) #Convert bit to bytes (1bit = 8bytes)
            accel_wavfile.setframerate(self.sampling_rate)
            #accel_wavfile.setframerate(self.sampling_rate*self.sampling_duration)


            data_array = array.array('f', accel_values)
            # Other method for array conversion - numpy
            # normalised_data = (accel_values - np.min(accel_values))/(np.max(accel_values) - np.min(accel_values))
            # normalised_data = (normalised_data * (2**(self.adc_bitdepth))).astype(np.int16)
            accel_wavfile.writeframes(data_array.tobytes())

        return data.AccelRecording(
            datetime=recording_starttime,
            hwid=hwid_accel,
            path=Path(final_file_path),
        )
        spi.close()
