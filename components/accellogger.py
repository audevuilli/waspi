""" This app records a two channel WAV file which records the output from the
    two nest accelerometers.

   Peter Willison 9th September 2021
"""

# Force the use of Python 3 interpreter
#! /usr/bin/env python3

from datetime import datetime
import time
import os
import sys
import sounddevice as sd
from scipy.io.wavfile import write

# The file path to the data folder on the local machine
#outputFolder = '/home/pi/Documents/A_Up_Wasps/nest1/accelOutput/'
outputFolder = '/waspi/components/accelOutput'

# How often does a recording start, in seconds?
checkInterval = 120

# Duration of recording, in seconds
duration = 10

# Audio sample rate
sampleFreq = 44100


###################################################################################################

def recordAudioFile(fileName):
    myrecording = sd.rec(int(duration * sampleFreq), samplerate=sampleFreq, channels = 2)
    sd.wait()
    write(fileName + '.tmp', sampleFreq, myrecording)


###################################################################################################

def main():
    
    try:
        while True:
            dateTimeNow = datetime.now()
            filename = "accelAudio_%02d%02d%04d_%02d%02d%02d" % (dateTimeNow.day, dateTimeNow.month, dateTimeNow.year, dateTimeNow.hour, dateTimeNow.minute, dateTimeNow.second)
            
            fullFilePath = outputFolder + filename
        
            recordAudioFile(fullFilePath)
            
            # Clear the terminal window
            os.system('clear')
            
            # Rename yesterday's file to a .txt file so that it is uploaded to Dropbox by waspFileWatcher
            os.rename(fullFilePath + '.tmp', fullFilePath + '.wav')
            
            print ("Last WAV file generated - " + str(time.asctime(time.gmtime())))
            print ("Next WAV file to be generated in " + str(checkInterval) + " seconds")

            time.sleep(checkInterval)
        
    except Exception as e:
        print ('Hmm, something broke : ', e)       
        

###################################################################################################

if __name__ == '__main__':
    main()
