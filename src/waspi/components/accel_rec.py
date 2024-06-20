"""Accelerometers Recorder using HifiBerry Board."""
import datetime
#import time
#import os
from pathlib import Path
import sys
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np

from waspi import data
from waspi.components.types import AudioRecorder


class AccelRecorder(AudioRecorder):
    """An AccelRecorder that record 2-channels audio file."""
    duration = float
    """The duration of the audio file in seconds."""

    samplerate: int
    """The samplerateof the audio file in Hz."""

    audio_channels: int
    """The number of audio channels."""

    #device_name: str
    #"""The name of the input audio device."""

    audio_dir: Path
    """The path of the audio file in temporary memory."""

    def __init__(
        self,
        duration: float,
        samplerate: int,
        audio_channels: int,
        #device_name: str,
        audio_dir: Path,
    ) -> None:
        """Initialise the AudioRecorder with the audio parameters."""
        # Audio Duration
        self.duration = duration

        # Audio Microphone Parameters
        self.samplerate = samplerate
        self.audio_channels = audio_channels
        #self.device_name = device_name

        # Audio Files Parameters
        self.audio_dir = audio_dir
         
    def record(self) -> data.Recording:
        """Record an audio file reading values from the accelerometers. 
        Use the HiFiBerry DAC+ ADC Board as audio interface to the RPI. 
        """
        now = datetime.datetime.now()
        audiofile_path = self.audio_dir / f'{now.strftime("%Y%m%d_%H%M%S")}.wav'
        
        # Find information about the selected device
        devices_list = sd.query_devices()
        print(f"Recording Devices List: {devices_list}")
        info = sd.check_input_settings()
        print(f"Recording Device Settings: {info}")

        # Define Sounddevice Parameters
        sd.default.samplerate = self.samplerate
        #sd.default.channels = self.audio_channels
        default_device = sd.default.device 
        print(f"SD Default Device: {default_device}")

        try:
            myrecording = sd.rec(int(self.duration * self.samplerate),
                                 channels=self.audio_channels)
            sd.wait()
            write(audiofile_path, self.samplerate, myrecording)

        except Exception as e:
            print(f"Error during recording: {e}")
            return None

        return data.Recording(
            path=audiofile_path,
            datetime=now,
            duration=self.duration,
            samplerate=self.samplerate,
            audio_channels=self.audio_channels,
        )

