#!/bin/bash

REPO_DIR="/home/chris/rpi-long-range-video-transmission"
TRANSMISSION_SERVICE_NAME="video-transmission.service"
OLDE_STATUS_SERVICE_NAME="oled-status.service"

cd "$REPO_DIR" || exit 1

if ! ping -c 1 -W 2 8.8.8.8 > /dev/null 2>&1; then
    echo "$(date): No Internet connection. Skipping update."
    exit 0
fi

git fetch origin main

LOCAL_SHA=$(git rev-parse HEAD)
REMOTE_SHA=$(git rev-parse origin/main)

if [ "$LOCAL_SHA" != "$REMOTE_SHA" ]; then
    echo "$(date): Update detected. Pulling latest..."
    git reset --hard origin/main

    # restart the transmission service
    sudo systemctl restart "$TRANSMISSION_SERVICE_NAME"
    echo "$(date): Restarted $TRANSMISSION_SERVICE_NAME."

    # restart the oled status service
    sudo systemctl restart "$OLDE_STATUS_SERVICE_NAME"
    echo "$(date): Restarted $OLDE_STATUS_SERVICE_NAME."
else
    echo "$(date): No update needed."
fi
