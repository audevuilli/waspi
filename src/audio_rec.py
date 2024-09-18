import time
import datetime
import logging
import asyncio
from pathlib import Path

from waspi.components.audio import PyAudioRecorder

# Setup the main logger
logging.basicConfig(
    filename="waspi.log",
    filemode="w",
    format="%(levelname)s - %(message)s",
    level=logging.INFO,
)

##############################################
### CONFIGURATION PARAMETERS

AUDIO_SAMPLERATE = 44100
AUDIO_DURATION = 120
AUDIO_CHUNKSIZE = 4096
AUDIO_CHANNEL = 1
AUDIO_DEVICE_NAME = "WordForum USB: Audio"
AUDIO_DIR_PATH = Path.home() / "storages" / "recordings" / "audio_mic"

###############################################
### CREATE SENSOR OBJECTS
"""Create the Microhpone object."""
audio_mic = PyAudioRecorder(
    duration=AUDIO_DURATION,
    samplerate=AUDIO_SAMPLERATE,
    audio_channels=AUDIO_CHANNEL,
    device_name=AUDIO_DEVICE_NAME,
    chunksize=AUDIO_CHUNKSIZE,
    audio_dir=AUDIO_DIR_PATH,
)

##############################################
### DEFINE RUNNING PROCESSES


# Audio Microphone Process - Every 10 minutes
def record_audio():
    global first_reading_after_audio
    while True:
        logging.info(f" --- START AUDIO RECORDING {datetime.datetime.now()} --- ")
        audio_mic.record()
        logging.info(f" --- END AUDIO RECORDING {datetime.datetime.now()} ----")
        first_reading_after_audio = True
        time.sleep(1)


record_audio()
