#!/bin/bash

if ! cmp -s oled-status.service /etc/systemd/system/oled-status.service; then
    echo "Copying OLED status service file..."
    sudo cp oled-status.service /etc/systemd/system/

    echo "Reloading systemd daemon..."
    sudo systemctl daemon-reexec
    sudo systemctl daemon-reload

    echo "Enabling OLED status service..."
    sudo systemctl enable oled-status

    echo "Starting OLED status service..."
    sudo systemctl start oled-status
else
    echo "OLED status service already setup and no file changes; skipping"
fi

echo "Done!"
