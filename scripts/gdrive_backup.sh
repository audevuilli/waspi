#!bin/bash

# rclone sync variables
rcloneName="gdrive"
syncRoot="${HOME}"
DirImages="images"
DirRecordingsAccel="storages/recordings/accel_rec"
DirRecordingsMic="storages/recordings/audio_mic"
remoteSyncDir="waspi_backup"

# Get the date and folder_path of files to copy to gdrive
date_now=$(date +'%Y_%m_%d')

# Local Directories - RPi files paths to sync
localSyncImages_Path="${syncRoot}/${DirImages}/"
localSyncRecAccel_Path="${syncRoot}/${DirRecordingsAccel}/"
localSyncRecMic_Path="${syncRoot}/${DirRecordingsMic}/"
#echo "$localSyncRecMic_Path"

#Use rclone to copy folder over to gdrive
rclone copy $localSyncImages_Path $rcloneName:$remoteSyncDir/$DirImages/$date_now
rclone copy $localSyncRecAccel_Path $rcloneName:$remoteSyncDir/$DirRecordingsAccel/$date_now
rclone copy $localSyncRecMic_Path $rcloneName:$remoteSyncDir/$DirRecordingsMic/$date_now

#Delete files saved on gdrive
#rm -rf "$localSyncImages_Path"
rm "$DirRecordingsAccel/"*.wav
rm "$DirRecordingsMic/"*.wav
