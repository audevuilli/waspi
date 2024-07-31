"""AudioRecorder using USB Microphone for waspi."""
import datetime
import wave
from pathlib import Path
from typing import Optional

import pyaudio

from waspi import data
from waspi.components.types import AudioRecorder

class PyAudioRecorder(AudioRecorder):
    """An AudioRecorder that records a 3 second audio file."""

    duration: float
    """The duration of the audio file in seconds."""

    samplerate: int
    """The samplerateof the audio file in Hz."""

    audio_channels: int
    """The number of audio channels."""

    device_name: str
    """The name of the input audio device."""

    chunksize: int
    """The chunksize of the audio file in bytes."""

    audio_dir: Path
    """The path of the audio file in temporary memory."""

    def __init__(
        self,
        duration: float,
        samplerate: int,
        audio_channels: int,
        device_name: str,
        chunksize: int,
        audio_dir: Path,
    ) -> None:
        """Initialise the AudioRecorder with the audio parameters."""
        # Audio Duration
        self.duration = duration

        # Audio Microphone Parameters
        self.samplerate = samplerate
        self.audio_channels = audio_channels
        self.device_name = device_name

        # Audio Files Parameters
        self.chunksize = chunksize
        self.audio_dir = audio_dir
        self.sample_width = pyaudio.get_sample_size(pyaudio.paInt16)

        #if self.device_index is None:
            # Get the index of the audio device
        self.device_index = self.get_device_index()
        #self.device_index = device_index

    def get_device_index(self) -> int:
        """Get the index of the audio device."""
        # Create an instance of PyAudio
        p = pyaudio.PyAudio()
    
        # Get the number of audio devices
        num_devices = p.get_device_count()
        
        # Loop through the audio devices
        for i in range(num_devices):
            print(f"Device Number: {i}")
            # Get the audio device info
            device_info = p.get_device_info_by_index(i)
            print(f"DEVICE INFO: {device_info}")
            # Check if the audio device is an input device
            if not self.device_name in str(device_info["name"]):
                continue

            else:
                # Get the index of the USB audio device
                print(f"DEVICE INDEX: {device_info['index']}")
                device_index = int(device_info["index"])
                print(f"RETURN DEVICE_INDEX: {device_index}")
            
            return device_index

        raise ValueError("No USB audio device found")

    def record(self) -> data.Recording:
        """Record an audio file.

        Return the temporary path of the file.
        """
        now = datetime.datetime.now()
        audiofile_path = self.audio_dir / f'{now.strftime("%Y%m%d_%H%M%S")}.wav'
        frames = self.get_recording_data(duration=self.duration)
        self.save_recording(frames, audiofile_path)
        return data.Recording(
            path=audiofile_path,
            datetime=now,
            duration=self.duration,
            samplerate=self.samplerate,
            audio_channels=self.audio_channels,
            chunksize=self.chunksize,
        )

    def get_recording_data(
        self,
        duration: Optional[float] = None,
        num_chunks: Optional[int] = None,
    ) -> bytes:
        if num_chunks is None:
            if duration is None:
                raise ValueError("duration or num_chunks must be provided")

            num_chunks = int(duration * self.samplerate / self.chunksize)

        p = pyaudio.PyAudio()

        stream = p.open(
            format=pyaudio.paInt16,
            channels=self.audio_channels,
            rate=self.samplerate,
            input=True,
            frames_per_buffer=self.chunksize,
            input_device_index=self.device_index,
        )

        frames = []
        for _ in range(0, num_chunks if num_chunks > 0 else 1):
            audio_data = stream.read(
                self.chunksize,
                exception_on_overflow=True,
            )
            frames.append(audio_data)

        stream.stop_stream()
        stream.close()
        p.terminate()

        return b"".join(frames)

    def save_recording(self, data: bytes, path: Path) -> None:
        """Save the recording to a file."""
        with wave.open(str(path), "wb") as audio_file:
            audio_file.setnchannels(self.audio_channels)
            audio_file.setsampwidth(self.sample_width)
            audio_file.setframerate(self.samplerate)
            audio_file.writeframes(data)

