#!/usr/bin/python3

import datetime
import time
import arrow
import numpy as np
from pathlib import Path

from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput
from PIL import Image

from camera_settings import *

# conversion from stream coordinate to full image coordinate
X_MO_CONV = imageWidth/float(streamWidth)
Y_MO_CONV = imageHeight/float(streamHeight)


#------------------------------------------------------------------------------
def get_now():
    """ Get datetime and return formatted string"""
    now = datetime.datetime.now()
    return ("%04d%02d%02d-%02d:%02d:%02d"
            % (now.year, now.month, now.day,
               now.hour, now.minute, now.second))


#------------------------------------------------------------------------------
def check_image_dir(images_dir):
    """ if image_dir does not exist create the folder """
    date_today = datetime.datetime.today().strftime('%Y_%m_%d')
    images_dir_date = Path(images_dir) / f"{date_today}"

    if not images_dir_date.exists():
        try:
            images_dir_date.mkdir(parents=True)
        except OSError as err:
            print("ERROR : Could Not Create Folder %s %s" % (images_dir_date, err))
            exit(1)

    return images_dir_date

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
def get_image_filename(images_dir, image_name_prefix, current_count):
    """
    Create a file name based on settings.py variables. Save images in datetime.
    """
    if imageNumOn:
        file_path = images_dir+ "/"+image_name_prefix+str(current_count)+".jpg"
    else:
        datetime_now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        file_path = str(images_dir) + '/' + str(datetime_now) + '.jpg'
    return file_path

def get_video_filename(video_dir, video_name_prefix, current_count):
    """
    Create a file name based on settings.py variables. Save images in datetime.
    """
    datetime_now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    file_path = str(video_dir) + '/' + str(datetime_now) + '.jpg'
    return file_path

#------------------------------------------------------------------------------
def is_time_to_record():
    """Check if the current time is within the recording window."""
    current_hour = datetime.datetime.now().hour
    return videoRecordStartHour <= current_hour < videoRecordEndHour

#------------------------------------------------------------------------------
def get_last_counter():
    """
    glob imagePath for last saved jpg file. Try to extract image counter from
    file name and convert to integer.  If it fails restart number sequence.

    Note: If the last saved jpg file name is not in number sequence name
    format (example was in date time naming format) then previous number
    sequence images will be overwritten.

    Avoid switching back and forth between datetime and number sequences
    per imageNumOn variable in settings.py
    """
    counter = imageNumStart
    if imageNumOn:
        image_ext = ".jpg"
        search_str = imagePath + "/*" + image_ext
        file_prefix_len = len(imagePath + imageNamePrefix)+1
        try:
           # Scan image folder for most recent jpg file
           # and try to extract most recent number counter from file name
            newest = max(glob.iglob(search_str), key=os.path.getctime)
            count_str = newest[file_prefix_len:newest.find(image_ext)]
            print("%s INFO  : Last Saved Image is %s Try to Convert %s"
                  % (get_now(), newest, count_str))
            counter = int(count_str)+1
            print("%s INFO  : Next Image Counter is %i"
                  % (get_now(), counter))
        except:
            print("%s WARN  : Restart Numbering at %i "
                  "WARNING: Previous Files May be Over Written."
                  % (get_now(), counter))
    return counter


#------------------------------------------------------------------------------
def take_day_image(image_path):
    with Picamera2() as camera:
        camera.resolution = (imageWidth, imageHeight)
        camera.vflip = imageVFlip
        camera.hflip = imageHFlip
        camera.exposure_mode = 'auto'
        camera.awb_mode = 'auto'
        time.sleep(1)
        camera.start()
        try:
            image_array = camera.capture_array()
        except Exception as e:
            print(f"Exception: {e}")
        camera.stop()

        if image_array is None:
            print("Error")

        image = Image.fromarray(image_array).convert('RGB')
        image.save(image_path)

        return image_path

#------------------------------------------------------------------------------
def get_stream_array():
    """ Take a stream image and return the image data array"""
    with Picamera2() as camera:
        camera.resolution = (streamWidth, streamHeight)
        camera.vflip = imageVFlip
        camera.hflip = imageHFlip
        camera.exposure_mode = 'auto'
        camera.awb_model = 'auto'
        time.sleep(1)
        camera.start()
        try:
            image = camera.capture_array()
        except Exception as e:
            print(f"Exception: {e}")

        camera.stop()
        #print(f"GET STREAM ARRAAY IMAGE: {image}")

        return image

#------------------------------------------------------------------------------
def scan_motion():
    """ Loop until motion is detected """
    data1 = get_stream_array()
    while True:
        data2 = get_stream_array()
        diff_count = 0
        for y in range(0, streamHeight):
            #print(y)
            for x in range(0, streamWidth):
                #print(x)
                # get pixel differences. Conversion to int
                # is required to avoid unsigned short overflow.
                diff = abs(int(data1[y][x][1]) - int(data2[y][x][1]))
                if  diff > threshold:
                    diff_count += 1
                    if diff_count > sensitivity:
                        # x,y is a very rough motion position
                        return x, y
        data1 = data2


#-----------------------------------------------------------------------------
def do_motion_detection():
    """
    Loop until motion found then take an image,
    and continue motion detection. ctrl-c to exit
    """
    current_count = get_last_counter()
    imageDir=check_image_dir(imagePath)
    if not imageNumOn:
        print("%s INFO  : File Naming by Date Time Sequence" % get_now())
    while True:
        x_pos, y_pos = scan_motion()
        file_name = get_file_name(imageDir, imageNamePrefix, current_count)
        take_day_image(file_name)
        if imageNumOn:
            current_count += 1
        # Convert xy movement location for full size image
        mo_x = x_pos * X_MO_CONV
        mo_y = y_pos * Y_MO_CONV
        print("%s INFO  : Motion xy(%d,%d) Saved %s (%ix%i)"
              % (get_now(), mo_x, mo_y, file_name,
                 imageWidth, imageHeight,))


# Start Main Program Logic
if __name__ == '__main__':
    try:
        do_motion_detection()
    except KeyboardInterrupt:
        print("")
        print("INFO  : User Pressed ctrl-c")
        print("        Exiting %s %s " % (PROG_NAME, PROG_VER))


