# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT
# https://github.com/adafruit/Adafruit_CircuitPython_ADS1x15/blob/main/examples/ads1x15_fast_read.py

# Adapted and extended by Jolyon and Peter Willison - August 2021

# v2 - Reads all four channels but only trims and averages the load cell data - This has been done as on a RPi3 reading, trimming and averaging all
# four channels takes between 5 and 10 seconds

# Chan0 = wasp box
# Chan1 = control load cell
# Chan2 = Nest temperature sensor
# Chan4 = Shed temperature sensor

# Force the use of the Python 3 interpreter
#! /usr/bin/env python3

import time
import board
import busio
import os
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.ads1115 import Mode
from adafruit_ads1x15.analog_in import AnalogIn

# constant conversion for LMT87 - T1 = 0, T2 = 40, V1 = 2633, V2 = 2095
T1 = 0
T2 = 40
V1 = 2633
V2 = 2095
# Calculate this once
TEMP_CONVERSION_CONST = (V2 - V1) / (T2 - T1)

# Filepath for the data file
filePath = '/media/pi/DE8C7C8D8C7C6247/nest1/ADS1115Data/'

# The number of times the load cell value is read for each actual measurement. i.e. 1000 load cell values will
# be read and then averaged to obtain an actual measurement
readSamples = 1000

# Read Weight period - seconds
readPeriod = 10

# Gain set by ads.gain must be one of these values
gains = (2 / 3, 1, 2, 4, 8, 16)

# Data rate must be one of: [8, 16, 32, 64, 128, 250, 475, 860] samples per second
rates = [8, 16, 32, 64, 128, 250, 475, 860] 

# Create the I2C bus with a fast frequency.  Raspberry Pis must change this in /boot/config.txt
i2c = busio.I2C(board.SCL, board.SDA, frequency=1000000)

# Create the ADC object using the I2C bus
ads = ADS.ADS1115(i2c)

# ADC set to Continuous mode - This is only recommended when reading a single pin (channel)
# So, we should use the differential mode and only read one value from the A2D if possible?
ads.mode = Mode.CONTINUOUS

# Configure ADC Inputs

# Configure channel 0 - Box load cell
chan0 = AnalogIn(ads, ADS.P0)

# Configure channel 1 - Control load cell
chan1 = AnalogIn(ads, ADS.P1)

# Configure channel 2 - 3v3 reference
chan2 = AnalogIn(ads, ADS.P2)

# Configure channel 3 - analogue temperature
chan3 = AnalogIn(ads, ADS.P3)

# Data rate = 860
ads.data_rate = rates[7]

# PGA Gain setting = 1
ads.gain = gains[1]

# Actually configure the device by sending a read command
# First ADC channel read configures device and waits 2 conversion cycles
_ = chan0.value

# The period to wait between each of the SAMPLES to ensure the ADC has settled
sample_interval = 1.0 / ads.data_rate

repeats = 0
skips = 0

#create an array of zeros ready to receive the data from the ADC
loadCell0_Buffer = [0 for i in range(readSamples)]
loadCell1_Buffer = [0 for i in range(readSamples)]
#voltage_Buffer = [0 for i in range(readSamples)]
#analogueTemp_Buffer = [0 for i in range(readSamples)]



###################################################################################################

def ReadValues(channelA, channelB, channelC, channelD, sampleCount):
    ''' Reads 'SampleCount' values from the a2d from the hx711 as fast as possible into an array then trims extreme values
    (usually due to messed up bytes) and returns the average.  Roughly 85ms per sample'''
    
    # Snapshot of time of start of sampling
    start = time.monotonic()
    
    # The time to take the next sample value
    time_next_sample = start + sample_interval
    
    # Now read the load cell 'SampleCount' number of times
    # Need to allow a period (sample_interval) between readings to allow the ADC to take the next reading
    for i in range(0, sampleCount):
        while time.monotonic() < (time_next_sample):
            # wait for the next reading to become available
            pass
        
        # Read the raw a2d value and overwrite any values in the readingsBuffer
        loadCell0_Buffer[i] = channelA.value
        loadCell1_Buffer[i] = channelB.value
        
        # Loop timing to ensure ADC value is valid
        time_last_sample = time.monotonic()
        time_next_sample = time_next_sample + sample_interval
        if time_last_sample > (time_next_sample + sample_interval):
            # Skip a sample_interval amount of time as the last value wasn't read fast enough
            time_next_sample = time.monotonic() + sample_interval
        
    # Calculate a trim value, i.e. remove 5% of the highest and lowest values
    trimAmount = int(sampleCount * 0.05)
    
    # Sort the lists of values in ascending order
    loadCell0_Buffer.sort()
    loadCell1_Buffer.sort()
    #voltage_Buffer.sort()
    #analogueTemp_Buffer.sort()
    
    # Remove the 'TrimAmount' of extreme high and low values
    trimmedBuffer0 = loadCell0_Buffer[trimAmount:-trimAmount]
    trimmedBuffer1 = loadCell1_Buffer[trimAmount:-trimAmount]
    #trimmedBuffer2 = voltage_Buffer[trimAmount:-trimAmount]
    #trimmedBuffer3 = analogueTemp_Buffer[trimAmount:-trimAmount]
    
    
    # Calculate the average value of the trimmed values - Jolyon - why the * 10??
    result = [0 for i in range(4)]
    result[0] = int(10*sum(trimmedBuffer0)/len(trimmedBuffer0))
    result[1] = int(10*sum(trimmedBuffer1)/len(trimmedBuffer1))
    
    # Read instantaneous voltage value
    result[2] = channelC.value
    
    # Read instantaneous analogue temp value
    result[3] = channelD.value
    
    #result[2] = int(10*sum(trimmedBuffer2)/len(trimmedBuffer2))
    #result[3] = int(10*sum(trimmedBuffer3)/len(trimmedBuffer3))
    
    return result

### End of ReadWeight function ####################################################################

def convertTemp(AdcValue):
    # Convert the output from the ADC for the temperature channels to degC
    # Temp sensor is LMT87
    # Output is 13.6mV / degC
    # With a gain setting = 1 the ADC1115 has a Full Scale output of 4.096V
    # ADC115 is 16bit and full scale positive is 7FFFh = 32767
    # Therefore actual voltage output from sensor = ADC Reading / 32767 * 4.096
    # This function uses the linear approximaion conversion as described in the datasheet

    # N.B. sensorVoltage has to be in mV so * 1000
    sensorVoltage = AdcValue / 32767 * 4.096 * 1000
    
    actualTemp = ((sensorVoltage - V1) / TEMP_CONVERSION_CONST) + T1
    
    actualTemp = round(actualTemp, 4)
    
    return actualTemp
    

###################################################################################################

def outputDataToTerminal(values, differential, ratio):
    # Create terminal output string
    borderStr = '==========================================================================================='
    dateTimeStr = str(time.asctime(time.gmtime()))
    headerStrRow1 = ' Box Load   |   Control Load   | Nest Temp | Shed Temp |  Control - Box  | Control / Box |'
    headerStrRow2 = '            |                  |   deg C   |   deg C   |                 |               |'  
            
    print (borderStr, end = "\n")
    print (dateTimeStr, end = "\n")
    print (borderStr, end = "\n")
    print (headerStrRow1, end = "\n")
    print (headerStrRow2, end = "\n")
    print ('   ' + str(values[0]) + '           ' + str(values[1]) + '        ' + str(values[2]) + '      ' + str(values[3]) + '         ' + str(differential) + '          ' + ('%.4f' % ratio))
    print (borderStr, end = "\n")
            
###################################################################################################
    
    
def main():

    # The program starts here
    print("Started - " + time.asctime(time.gmtime()) + ' UTC')

    # Wait for the pi to load the external drive
    time.sleep(10)

    # Snapshot value for the start time
    readStart = time.monotonic()
    nextReadTime = readStart + readPeriod

    # Create initial filename based on DateTime
    filename = filePath + time.strftime("%a %b %d %Y", time.gmtime())

    # Take snapshot of today's date
    today = time.gmtime().tm_mday

    # Open the file, in append mode, to save the differential weight values to
    FileObject=open(filename + '.tmp', "a", 1)

    while True:
        try:
            if (time.monotonic() > nextReadTime):
                # Get the weight value
                values = ReadValues(chan0, chan1, chan2, chan3, readSamples)
            
                # Subtract the box load cell value from the control load cell
                differential = values[1] - values[0]
            
                ratio = values[1] / values[0]
                
                # Convert temp sensor output to actual degC
                values[2] = convertTemp(values[2])
                values[3] = convertTemp(values[3])
        
                # Clear the terminal window
                os.system('clear')
                
                # Output data to Terminal
                outputDataToTerminal(values, differential, ratio)
            
                OutputString = str(time.asctime(time.gmtime()) + "," + str(values[0]) + "," + str(values[1]) + "," + str(differential) + "," + str(values[2]) + "," + str(values[3]))
            
                # Write values to file
                FileObject.write(OutputString + "\n")
            
                # Calculate the next read time
                nextReadTime = nextReadTime + readPeriod
            
                # If midnight has passed then close current file and open a new file
                if (today != time.gmtime().tm_mday):

                    # Close the current data file
                    FileObject.close()
                    # Rename yesterday's file to a .txt file so that it is uploaded to Dropbox by waspFileWatcher
                    os.rename(filename + '.tmp', filename + '.txt')
            
                    # Create next days filename based on DateTime
                    filename = filePath + time.strftime("%a %b %d %Y", time.gmtime())
        
                    # Open the file, in append mode, to save the differential weight values to
                    FileObject=open(filename + '.tmp', "a", 1)
                
                    # Take snapshot of today's date
                    today = time.gmtime().tm_mday
            
            
        except (KeyboardInterrupt, SystemExit):
            FileObject.close()

###################################################################################################
        
if __name__ == "__main__":
    main()