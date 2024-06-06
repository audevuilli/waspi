import datetime
import time
import spidev
import os
import wave
import array
import signal
import sys
import asyncio

from pathlib import Path


class AccelLogger():
    """ Sample data from the accelerometer.
        Save the file into a .wav file. 

        MCP3002 SPI Communication:
        1. START transmission: CS HIGH/LOW
        2. SGL/DIFF: Select single-ended (1) or differential (0)
        3. ODD/SIGN: Select input channel
        4. MSBF: Enable LSB format first
    """

    def __init__(
        self,
        spi_channel: int, 
        spi_max_speed_hz: int, 
        vref: float, 
        adc_channel: int, 
        adc_bitdepth: int, 
        sampling_rate: int,
        sampling_duration: int,
    ):

        self.spi_channel = spi_channel
        self.spi_max_speed_hz = spi_max_speed_hz
        self.vref = vref
        self.adc_channel = adc_channel
        self.adc_bitdepth = adc_bitdepth
        self.sampling_rate = sampling_rate  #8000 Hz - maximum of 8000Hz 
        self.sampling_duration = sampling_duration 

    def read_adc(self, spi):

        if self.adc_channel != 0:
            self.adc_channel = 1

        msg = 0b11
        msg = ((msg << 1) + self.adc_channel) << 5
        msg = [msg, 0b00000000]
        reply = spi.xfer2(msg)

        adc = (reply[0] << 8) + reply[1]
        # Last bit (0) is not part of ADC value, shift to remove it
        adc = adc >> 1

        # Calculate voltage form ADC value
        print(f"ADC VALUE: {adc}")
        voltage = (self.vref * adc) / (2**self.adc_bitdepth)
        print(f"VOLTAGE VALUE: {voltage}")

        return adc


    def record_file(self):

        # Enable SPI
        spi = spidev.SpiDev(0, self.spi_channel)
        spi.max_speed_hz = self.spi_max_speed_hz

        # Check and create folder to store file
        recording_folder = Path.home() / "recordings" / "accelRecordings"
        recording_day = datetime.datetime.today().strftime('%Y_%m_%d')
        output_folder = Path(recording_folder) / f"{recording_day}"
        print(f"OUTPUT FOLDER: {output_folder}")

        if not output_folder.exists():
            output_folder.mkdir(parents=True)

        # Create the file path using the recording start time.
        hwid_accel = "accel"+str(self.adc_channel)
        #final_file_path = Path(output_folder) / f"{hwid_accel + '_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        final_file_path = str(output_folder) + '/' + str(hwid_accel) + '_' + str(datetime.datetime.now().strftime('%Y%m%d_%H%M%S')) + '.wav'
        print(f"FINAL FILE PATH: {final_file_path}")

        # Empty Array to store accel values
        adc_values = []

        # Get the starttime
        start_time = time.time()

        while time.time() - start_time < self.sampling_duration:
            adc_value = self.read_adc(spi)
            # print(f"ACCEL DATA: {data_accel}")
            adc_values.append(adc_value)

        # Convert accel_values to int suitable for .wav
        #scaling_factor = (2**(self.adc_bitdepth)-1) / self.vref
        #wav_data = [int(value * scaling_factor) for value in accel_values]
        print(f"WAV DATA: {adc_values}")


        with wave.open(final_file_path, "wb") as accel_wavfile:
            accel_wavfile.setnchannels(1)
            #accel_wavfile.setsampwidth(self.adc_bitdepth // 8)
            accel_wavfile.setsampwidth(2)
            accel_wavfile.setframerate(self.sampling_rate)

            data_array = array.array('f', adc_values)
            print(f"DATA ARRAY: {data_array}")
            accel_wavfile.writeframes(data_array.tobytes())
            #accel_wavfile.writeframes(wav_data)

        spi.close()
        print(f"Recording save to : {final_file_path}")

        return(start_time,
               hwid_accel,
               Path(final_file_path))


if __name__ == "__main__":
    
    accel_logger_1 = AccelLogger(
        spi_channel = 0,
        spi_max_speed_hz = 1200000,
        vref = 3.3,
        adc_channel = 1,
        adc_bitdepth=10,
        sampling_rate=16000,
        sampling_duration=10,
    )
    
    accel_logger_1.record_file()
    
    accel_logger_0 = AccelLogger(
        spi_channel = 0,
        spi_max_speed_hz = 1200000,
        vref = 3.3,
        adc_channel = 0,
        adc_bitdepth=10,
        sampling_rate=16000,
        sampling_duration=10,
    )

    accel_logger_0.record_file()
