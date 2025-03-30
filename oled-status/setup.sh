#!/bin/bash

echo "Copying OLED status service file..."
sudo cp oled-status.service /etc/systemd/system/

echo "Reloading systemd daemon..."
sudo systemctl daemon-reexec
sudo systemctl daemon-reload

echo "Enabling OLED status service..."
sudo systemctl enable oled-status

echo "Starting OLED status service..."
sudo systemctl start oled-status

echo "Done!"
