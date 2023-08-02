"""
HX711 Load cell amplifier Python Library
Original source: https://gist.github.com/underdoeg/98a38b54f889fce2b237
Documentation source: https://github.com/aguegu/ardulibs/tree/master/hx711
Adapted by 2017 Jiri Dohnalek

README:

This version runs in python 3.x. It will first prompt the user to 
empty the scale. Then prompt user to place an item with a known weight
on the scale and input weight as INT. 

The offset and scale will be adjusted accordingly and displayed for
convenience.

The user can choose to [0] exit, [1] recalibrate, or [2] display the 
current offset and scale values and weigh a new item to test the accuracy
of the offset and scale values!
"""

import RPi.GPIO as GPIO
import time
import sys
from hx711 import HX711

# Define RPi GPIO Pin
DOUT_Pin = 5
SCK_Pin = 6

# Create the HX711 object
hx = HX711(DOUT_Pin, SCK_Pin, gain=128)


def cleanAndExit():
    print("Cleaning up...")
    GPIO.cleanup()
    print("Bye!")
    sys.exit()


def setup():
    """
    code run once
    """
    print("Initializing.\n Please ensure that the scale is empty.")
    scale_ready = False
    while not scale_ready:
        if (GPIO.input(hx.DOUT) == 0):
            scale_ready = False
        if (GPIO.input(hx.DOUT) == 1):
            print("Initialization complete!")
            scale_ready = True


def calibrate():
    readyCheck = input("Remove any items from scale. Press any key when ready.")
    offset = hx.read_average()
    print("Value at zero (offset): {}".format(offset))
    hx.set_offset(offset)
    print("Please place an item of known weight on the scale.")

    readyCheck = input("Press any key to continue when ready.")
    measured_weight = (hx.read_average()-hx.get_offset())
    item_weight = input("Please enter the item's weight in grams.\n>")
    scale = int(measured_weight)/int(item_weight)
    hx.set_scale(scale)
    print("Scale adjusted for grams: {}".format(scale))


def loop():
    """
    code run continuously
    """
    try:
        prompt_handled = False
        while not prompt_handled:
            val = hx.get_grams()
            hx.power_down()
            time.sleep(.001)
            hx.power_up()
            print("Item weighs {} grams.\n".format(val))
            choice = input("Please choose:\n"
                           "[1] Recalibrate.\n"
                           "[2] Display offset and scale and weigh an item!\n"
                           "[0] Clean and exit.\n>")
            if choice == "1":
                calibrate()
            elif choice == "2":
                print("\nOffset: {}\nScale: {}".format(hx.get_offset(), hx.get_scale()))
            elif choice == "0":
                prompt_handled = True
                cleanAndExit()
            else:
                print("Invalid selection.\n")
    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()


##################################

if __name__ == "__main__":

    setup()
    calibrate()
    while True:
        loop()
