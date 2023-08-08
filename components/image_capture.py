#!/usr/bin/python3
import datetime
import time
import arrow
import numpy as np

from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FileOutput

IMG_RESOLUTION = (1280, 720)
IMG_FRAMERATE = 16
IMG_FORMAT = 'jpeg'

lsize = (320, 240)
picam2 = Picamera2()
video_config = picam2.create_video_configuration(main={"size": IMG_RESOLUTION, "format": "RGB888"},
                                                 lores={"size": lsize, "format": "YUV420"})
picam2.configure(video_config)
encoder = H264Encoder(1000000)
picam2.encoder = encoder
picam2.start()

w, h = lsize
prev = None
encoding = False
ltime = 0

def get_file_path():
    timestamp = arrow.utcnow().datetime.timestamp()
    time_now = datetime.datetime.now()
    file_name = time_now.strftime("%Y%m%d_%H%M%S")

    return file_name

while True:
    cur = picam2.capture_buffer("lores")
    cur = cur[:w * h].reshape(h, w)
    if prev is not None:
        # Measure pixels differences between current and
        # previous frame
        mse = np.square(np.subtract(cur, prev)).mean()
        if mse > 7:
            if not encoding:
                #encoder.output = FileOutput(f"{int(time.time())}.h264")
                encoder.output = FileOutput(f"{get_file_path()}.h264")
                picam2.start_encoder(encoder)
                encoding = True
                print("New Motion", mse)
            ltime = time.time()
        else:
            if encoding and time.time() - ltime > 2.0:
                picam2.stop_encoder(encoder)
                encoding = False
    prev = cur


# def get_file_path():
#     timestamp = arrow.utcnow().datetime.timestamp()
#     time_now = datetime.datetime.now()
#     file_name = time_now.strftime("%Y%m%d_%H%M%S")
# 
#     return file_name
# 
# def capture_image():
# 
#     # Define photo name
#     timestamp = arrow.utcnow().datetime.timestamp()
#     time_now = datetime.datetime.now()
#     file_name = time_now.strftime("%Y%m%d_%H%M%S")
# 
#     file_path = file_name + '.jpg'
#     print(file_path)


