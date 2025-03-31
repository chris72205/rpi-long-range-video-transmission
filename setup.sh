#!/bin/bash

echo "Updating package list..."
sudo apt-get update

echo "Installing dependencies..."
sudo apt-get install -y python3-pip python3-opencv python3-aiohttp python3-picamera2 python3-pil i2c-tools
# not good I know, but venv takes too long to build/install picamera2
sudo pip3 install --break-system-packages adafruit-blinka adafruit-circuitpython-ssd1306

echo "Setting up OLED status service..."
./oled-status/setup.sh

echo "Setting up video transmission service..."
./video-transmission/setup.sh

echo "Done setting up services!"
