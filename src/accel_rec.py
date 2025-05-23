import time
import datetime
import logging
from pathlib import Path

from waspi.components.accel_rec import AccelRecorder

# Setup the main logger
logging.basicConfig(
    filename="waspi.log",
    filemode="w",
    format="%(levelname)s - %(message)s",
    level=logging.INFO,
)

##############################################
### CONFIGURATION PARAMETERS

ACCEL_SAMPLERATE = 44100
ACCEL_DURATION = 120
ACCEL_CHANNEL = 2
ACCEL_DIR_PATH = Path.home() / "storages" / "recordings" / "accel_rec"

###############################################
### CREATE SENSOR OBJECTS
"""Create the Accelerometer objects."""
accel_rec = AccelRecorder(
    duration=ACCEL_DURATION,
    samplerate=ACCEL_SAMPLERATE,
    audio_channels=ACCEL_CHANNEL,
    audio_dir=ACCEL_DIR_PATH,
)

##############################################
### DEFINE RUNNING PROCESSES


# Audio Microphone Process - Every 10 minutes
def record_accel():
    global first_reading_after_audio
    while True:
        logging.info(f" --- START AUDIO RECORDING {datetime.datetime.now()} --- ")
        accel_rec.record()
        logging.info(f" --- END AUDIO RECORDING {datetime.datetime.now()} ----")
        first_reading_after_audio = True
        time.sleep(0.1)


# Run the audio recording process continuously
record_accel()
