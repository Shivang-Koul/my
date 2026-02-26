#!/bin/bash

# Configuration
BACKUP_SOURCE="$HOME/Desktop"  # Folder to backup - change this to your desired folder
S3_DESTINATION="s3://cloudage.llc/backup"  # Your S3 bucket
LOG_FILE="$HOME/Desktop/s3_backup.log"  # Log file location

# AWS CLI profile (optional - remove if using default profile)
AWS_PROFILE="default"

# Timestamp for logging
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# Create log directory if it doesn't exist
mkdir -p "$(dirname "$LOG_FILE")"

echo "[$TIMESTAMP] Starting backup from $BACKUP_SOURCE to $S3_DESTINATION" >> "$LOG_FILE"

# Perform the sync
aws s3 sync "$BACKUP_SOURCE" "$S3_DESTINATION" \
  --profile "$AWS_PROFILE" \
  --delete \
  --exclude "*.DS_Store" \
  --exclude "*.tmp" \
  >> "$LOG_FILE" 2>&1

EXIT_STATUS=$?

# #uncomment if you want to upload multiple folders.

#DIRS=("$HOME/Documents" "$HOME/Pictures")
#for DIR in "${DIRS[@]}"; do
#   aws s3 sync "$DIR" "$S3_DESTINATION/$(basename "$DIR")" ...
#done

if [ $EXIT_STATUS -ne 0 ]; then
    mail -s "Backup Failed" khurram@cloudage.com.co < "$LOG_FILE"
fi

# Check exit status
if [ $EXIT_STATUS -eq 0 ]; then
    echo "[$(date +"%Y-%m-%d %H:%M:%S")] Backup completed successfully" >> "$LOG_FILE"
else
    echo "[$(date +"%Y-%m-%d %H:%M:%S")] Backup failed - check logs for details" >> "$LOG_FILE"
fi
