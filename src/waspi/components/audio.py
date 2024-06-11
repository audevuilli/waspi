"""AudioRecorder using USB Microphone for waspi."""

import datetime
import wave
from pathlib import Path
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
        logger=None,
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

        if logger is None:
            logger = get_task_logger(__name__)
        self.logger = logger
        
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

        device = self.get_input_device(p)

        stream = p.open(
            format=pyaudio.paInt16,
            channels=self.audio_channels,
            rate=self.samplerate,
            input=True,
            frames_per_buffer=self.chunksize,
            input_device_index=device.index,
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

    def get_input_device(self, p: pyaudio.PyAudio):
        """Get the input device."""
        print(self.device_name)
        print(type(self.device_name))
        input_devices = get_input_devices(p)
        device = next(
            (d for d in input_devices if d.name == self.device_name), None
        )

        for d in range(get_input_devices(p)):
            print(d)
            print(d.name)
            print(type(d.name))

        if device is None:
            raise ParameterError(
                value="device_name",
                message="The selected input device was not found.",
                help="Check if the microphone is connected.",
            )

        return device
