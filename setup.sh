#!/bin/bash

echo "Updating package list..."
sudo apt-get update

echo "Installing dependencies..."
sudo apt-get install -y python3-pip python3-opencv python3-aiohttp python3-picamera2

echo "Done!"
