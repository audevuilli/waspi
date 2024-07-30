import datetime
from pathlib import Path
import subprocess
import sys
from waspi import data
from waspi.components.types import AudioRecorder


class AccelRecorder(AudioRecorder):
    """An AccelRecorder that records a 2-channel audio file."""
    
    duration: float
    """The duration of the audio file in seconds."""
    
    samplerate: int
    """The samplerate of the audio file in Hz."""
    
    audio_channels: int
    """The number of audio channels."""
    
    audio_dir: Path
    """The path of the audio file in temporary memory."""

    def __init__(
        self, 
        duration: float, 
        samplerate: int, 
        audio_channels: int, 
        audio_dir: Path
    ) -> None:
        """Initialize the AudioRecorder with the audio parameters."""
        self.duration = duration
        self.samplerate = samplerate
        self.audio_channels = audio_channels
        self.audio_dir = audio_dir

    def record(self) -> data.Recording:
        """Record an audio file using arecord."""
        now = datetime.datetime.now()
        audiofile_path = self.audio_dir / f'{now.strftime("%Y%m%d_%H%M%S")}.wav'
        
        try:
            # Define the arecord command
            arecord_command = [
                'arecord',
                '-D', 'plughw:2,0',  # Replace with the correct device ID or name
                '--format=S16_LE',
                f'--channels={self.audio_channels}',
                f'--rate={self.samplerate}',
                f'--duration={int(self.duration)}',
                str(audiofile_path)
            ]
            
            # Run the command
            subprocess.run(command, check=True)
        
        except subprocess.CalledProcessError as e:
           #print(f"Error during recording: {e}")
           return None

        return data.Recording(
            path=audiofile_path,
            datetime=now,
            duration=self.duration,
            samplerate=self.samplerate,
            audio_channels=self.audio_channels,
        )
