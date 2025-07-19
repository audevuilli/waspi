#!/usr/bin/python3

import datetime
import time
from pathlib import Path

from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput

from camera_settings import *

#------------------------------------------------------------------------------
def get_now():
    """ Get datetime and return formatted string"""
    now = datetime.datetime.now()
    return ("%04d%02d%02d-%02d:%02d:%02d"
            % (now.year, now.month, now.day,
               now.hour, now.minute, now.second))


#------------------------------------------------------------------------------
def check_video_dir(video_path):
    """ if video_path does not exist create the folder """
    date_today = datetime.datetime.today().strftime('%Y_%m_%d')
    video_dir_date = Path(video_path) / f"{date_today}"

    if not video_dir_date.exists():
        try:
            video_dir_date.mkdir(parents=True)
        except OSError as err:
            print("ERROR : Could Not Create Folder %s %s" % (video_dir_date, err))
            exit(1)

    return video_dir_date

#------------------------------------------------------------------------------
def get_video_filenames(video_dir):
    """
    Create a file name based on settings.py variables. Save images in datetime.
    """
    datetime_now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    temp_path = str(video_dir) + '/' + str(datetime_now) + '_part.mp4'
    final_path = temp_path = str(video_dir) + '/' + str(datetime_now) + '.mp4'

    return final_path, temp_path

#------------------------------------------------------------------------------
def is_time_to_record():
    """Check if the current time is within the recording window."""
    current_hour = datetime.datetime.now().hour
    return videoRecordStartHour <= current_hour < videoRecordEndHour

#------------------------------------------------------------------------------
def record_video_chunk():
    """Records a single video chunk for the specified duration."""
    video_dir = check_video_dir(videoPath)
    #video_file = get_video_filename(video_dir)
    final_file, temp_file = get_video_filenames(video_dir)
    
    picam2 = Picamera2()
    try:
        print(f"{get_now()} INFO  : Configuring camera for video...")
        video_config = picam2.create_video_configuration(
            main={"size": (videoWidth, videoHeight)}
        )
        picam2.configure(video_config)
        picam2.options["quality"] = 95 # Set high quality for H.264
        
        # Set flips
        picam2.vflip = videoVFlip
        picam2.hflip = videoHFlip

        encoder = H264Encoder()
        output = FfmpegOutput(temp_file)

        print(f"{get_now()} INFO  : Starting video recording to {temp_file} for {videoDuration}s...")
        picam2.start_recording(encoder, output)
        time.sleep(videoDuration)
        picam2.stop_recording()

        # Atomically rename the temp file to the final name upon completion
        #final_file = temp_file.replace('_part', '')
        temp_file.rename(final_file)
        print(f"{get_now()} INFO  : Finished recording. Final file is {final_file}")

    except Exception as e:
        print(f"{get_now()} ERROR : An error occurred during recording: {e}")
    finally:
        if picam2.started:
            picam2.stop()
        picam2.close()
        print(f"{get_now()} INFO  : Camera closed.")

#------------------------------------------------------------------------------
def continuous_recording_loop():
    """
    Main loop to continuously record video in chunks during the scheduled time.
    """
    print(f"{get_now()} INFO  : Starting continuous recording service.")
    print(f"{get_now()} INFO  : Recording window is from {videoRecordStartHour}:00 to {videoRecordEndHour}:00.")
    
    while True:
        if is_time_to_record():
            record_video_chunk()
        else:
            print(f"{get_now()} INFO  : Outside recording window. Sleeping for 5 minutes.")
            time.sleep(300) # Sleep for 5 minutes before checking again

# Start Main Program Logic
if __name__ == '__main__':
    try:
        continuous_recording_loop()
    except KeyboardInterrupt:
        print("")
        print(f"{get_now()} INFO  : User Pressed ctrl-c. Exiting.")
    except Exception as e:
        print(f"{get_now()} ERROR : Application crashed: {e}")
        raise


