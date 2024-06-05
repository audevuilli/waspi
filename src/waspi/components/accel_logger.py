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
import numpy as np

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

        # Check and create folder to store file
        recording_folder = Path.home() / "recordings" / "accelRecordings"
        recording_day = datetime.today().strftime('%Y_%m_%d')
        output_folder = Path(recording_folder / f"{recording_day}"
        print(f"OUTPUT FOLDER: {output_folder}")

        if not output_folder.exists():
            output_folder.mkdir(parents=True)

        # Create the file path using the recording start time.
        hwid_accel = "accel"+str(self.adc_channel)
        final_file_path = Path(output_folder) / f"{hwid_accel + '_' + {datetime.datime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        print(f"FINAL FILE PATH: {final_file_path}")


        # Empty array to store the values
        accel_values = []

        # Get the start time 
        start_time = time.time()  # Get the start time

        while time.time() - start_time < self.sampling_duration:
            data_accl = self.read_adc(spi)
            accel_values.append(data_accl)

        # Convert accel_values to int suitable for .wav
        scaling_factor = (2**(self.adc_bitdepth)-1) / self.vref
        wav_data = [int(value * scaling_factor) for value in accel_values]

        # Create a WAV file to write the acceleromter values
        with wave.open(final_file_path, "wb") as accel_wavfile:
            accel_wavfile.setnchannels(1)
            accel_wavfile.setsampwidth(self.adc_bitdepth // 8) #Convert bit to bytes (1bit = 8bytes)
            accel_wavfile.setframerate(self.sampling_rate)
)
            accel_wavfile.writeframes(wav_data.tobytes())

        spi.close()

        return data.AccelRecording(
            datetime=recording_starttime,
            hwid=hwid_accel,
            path=Path(final_file_path),
        )
