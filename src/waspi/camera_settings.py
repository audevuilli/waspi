# User Configuration variable settings 
# Initial script by - Claude Pageau. Modified by Aude Vuilliomenet June 2024
# Exit of Wasp Box is on the top of the image (Y-Axis Top). Entry is (Y-Axis Bottom).
from pathlib import Path

configTitle = "picamera-motion Default Settings"
configName  = "settings.py"

# User Video Settings
# -------------------
videoPath = Path.home() / "storages" / "videos"    # Folder path to save videos
videoNamePrefix = 'vid-' # Prefix for all video file names.
videoDuration = 300     # Duration of each video chunk in seconds (5 minutes)
videoWidth = 1280       # Video resolution width
videoHeight = 720       # Video resolution height
videoVFlip = True       # Flip video Vertically
videoHFlip = False      # Flip video Horizontally

# Recording Schedule
# ------------------
videoRecordStartHour = 4  # Hour to start recording (4 AM)
videoRecordEndHour = 22 # Hour to stop recording (10 PM)

# User Image Settings
# -------------------
imagePath = Path.home() / "storages" / "images"    # Folder path to save images
imageNamePrefix = 'mo-' # Prefix for all image file names. Eg front-
imageWidth = 1280       # Final image width
imageHeight = 720       # Final image height
imageVFlip = True       # Flip image Vertically
imageHFlip = False      # Flip image Horizontally
imagePreview = True     # Set picamera preview False=off True=on
imageNumOn = False      # Image Naming True=Number sequence  False=DateTime
imageNumStart = 1000    # Start of number sequence if imageNumOn=True

# User Motion Detection Settings
# ------------------------------
threshold = 20     # How Much pixel changes
sensitivity = 25   # How many pixels change
streamWidth = 100  # motion scan stream Width
streamHeight = 80

