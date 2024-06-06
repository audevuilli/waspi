#!bin/bash

# rclone sync variables
rcloneName="gdrive"
syncRoot="${HOME}"
DirImages="images"
DirRecordingsAccel="recordings/accelRecordings"
DirRecordingsMic="recordings/microphone"
remoteSyncDir="waspi_backup"

# Get the date and folder_path of files to copy to gdrive
date_now=$(date +'%Y_%m_%d')
localSyncImages_Path="${syncRoot}/${DirImages}/${date_now}/"
echo "$localSyncImages_Path"

localSyncRecAccel_Path="${syncRoot}/${DirRecordingsAccel}/${date_now}/"
localSyncRecMic_Path="${syncRoot}/${DirRecordingsMic}/${date_now}/"

echo "$localSyncRecAccel_Path"

#Use rclone to copy folder over to gdrive
rclone copy $localSyncImages_Path $rcloneName:$remoteSyncDir/$DirImages/$date_now
rclone copy $localSyncRecAccel_Path $rcloneName:$remoteSyncDir/$DirRecordingsAccel/$date_now

#rclone copy "$accelrec_path" gdrive:waspi_backup/accelRecordings/"${accelrec_date}"

#Delete files saved on gdrive
#rm -rf "$localSyncImages_Path"
#rm -rf "$localSyncRecAccel_Path"
