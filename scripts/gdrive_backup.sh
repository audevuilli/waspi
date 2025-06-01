#!bin/bash

# Lock File path
LOCK_FILE="/tmp/waspi.lock"

# Function to aquire lock
acquire_lock() {
    exec 200>"$LOCK_FILE"
    if flock -n 200; then
        echo "Lock acquired for sync operation."
        return 0
    else
        echo "Could not acquire lock - main script is running."
        exit 1
    fi
}

# Function to release lock
release_lock() {
    flock -u 200
    rm -f "$LOCK_FILE"
    echo "Lock released."
}

# Trap to ensure lock is released on exit
trap release_lock EXIT

# Try to acquire the lock
if ! acquire_lock; then
    echo "Sync aborted - main script is running."
    exit 1
fi

echo "Starting sync operation..."

# rclone sync variables
rcloneName="gdrive"
syncRoot="${HOME}"
#DirImages="storages/images"
DirRecordingsAccel="storages/recordings/accel_rec"
remoteSyncDir="waspi_backup"

# Get the date and folder_path of files to copy to gdrive
date_now=$(date +'%Y_%m_%d')

# Local Directories - RPi files paths to sync
#localSyncImages_Path="${syncRoot}/${DirImages}/${date_now}"
localSyncRecAccel_Path="${syncRoot}/${DirRecordingsAccel}/"

#Use rclone to copy folder over to gdrive
#rclone copy $localSyncImages_Path $rcloneName:$remoteSyncDir/$DirImages/$date_now
rclone copy $localSyncRecAccel_Path $rcloneName:$remoteSyncDir/$DirRecordingsAccel/$date_now

# Check if rclone command was successful
if [ $? -eq 0 ]; then
    echo "Sync operation completed successfully."
    # Delete the files that were sync
    #rm -rf "$localSyncImages_Path"
    #rm -rf "$DirImages"
    rm "$DirRecordingsAccel/"*.wav
else
    echo "Rclone sync operation failed."
    exit 1
fi