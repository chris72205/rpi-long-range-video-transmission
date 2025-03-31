#!/bin/bash

REPO_DIR="/home/chris/rpi-long-range-video-transmission"

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

    # re-run the setup script in case any dependencies were updated
    $REPO_DIR/setup.sh

    # Read configured services from YAML file
    if [ -f "$REPO_DIR/configured_services.yml" ]; then
        # Extract enabled services and their directories
        while IFS= read -r line; do
            if [[ $line =~ ^[[:space:]]*([a-zA-Z0-9-]+):[[:space:]]*$ ]]; then
                service_name="${BASH_REMATCH[1]}"
                # Check if service is enabled
                if grep -A1 "^[[:space:]]*$service_name:" "$REPO_DIR/configured_services.yml" | grep -q "enabled: true"; then
                    service_file="$service_name.service"
                    echo "$(date): Restarting $service_file..."
                    sudo systemctl restart "$service_file"
                fi
            fi
        done < "$REPO_DIR/configured_services.yml"
    else
        echo "$(date): Warning: configured_services.yml not found. No services will be restarted."
    fi
else
    echo "$(date): No update needed."
fi
