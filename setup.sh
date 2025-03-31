#!/bin/bash

# Function to check if a service is enabled in configured_services.yml
is_service_enabled() {
    local service_name=$1
    if [ -f "configured_services.yml" ]; then
        grep -A1 "^  $service_name:" configured_services.yml | grep -q "enabled: true"
    else
        return 1
    fi
}

# Function to ask user about a service
ask_about_service() {
    local service_name=$1
    local description=$2
    local default=$3
    
    if [ -f "configured_services.yml" ] && is_service_enabled "$service_name"; then
        default="y"
    fi
    
    while true; do
        read -p "Would you like to enable $service_name? ($description) [Y/n] " yn
        case $yn in
            [Yy]* ) return 0;;
            [Nn]* ) return 1;;
            "" ) if [ "$default" = "y" ]; then return 0; else return 1; fi;;
            * ) echo "Please answer yes or no.";;
        esac
    done
}

echo "Updating package list..."
sudo apt-get update

echo "Installing dependencies..."
sudo apt-get install -y python3-pip python3-opencv python3-aiohttp python3-picamera2 python3-pil i2c-tools
# not good I know, but venv takes too long to build/install picamera2
sudo pip3 install --break-system-packages adafruit-blinka adafruit-circuitpython-ssd1306

# Create or update configured_services.yml
echo "Configuring services..."
if [ ! -f "configured_services.yml" ]; then
    # Create new file with default settings
    cat > configured_services.yml << EOL
services:
  oled-status:
    enabled: false
    description: "OLED status display showing system information"
    directory: "oled-status"
  
  video-transmission:
    enabled: false
    description: "Long range video transmission system"
    directory: "video-transmission"
EOL
else
    # Ensure all required services exist in the file
    if ! grep -q "^  oled-status:" configured_services.yml; then
        sed -i '/^services:/a\  oled-status:\n    enabled: false\n    description: "OLED status display showing system information"\n    directory: "oled-status"' configured_services.yml
    fi
    if ! grep -q "^  video-transmission:" configured_services.yml; then
        sed -i '/^services:/a\  video-transmission:\n    enabled: false\n    description: "Long range video transmission system"\n    directory: "video-transmission"' configured_services.yml
    fi
fi

# Ask about each service
if ask_about_service "oled-status" "OLED status display showing system information" "y"; then
    sed -i '/oled-status:/,/enabled:/ s/enabled: false/enabled: true/' configured_services.yml
    echo "Setting up OLED status service..."
    ./oled-status/setup.sh
fi

if ask_about_service "video-transmission" "Long range video transmission system" "y"; then
    sed -i '/video-transmission:/,/enabled:/ s/enabled: false/enabled: true/' configured_services.yml
    echo "Setting up video transmission service..."
    ./video-transmission/setup.sh
fi

echo "Done setting up services!"
