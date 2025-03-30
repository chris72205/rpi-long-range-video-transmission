#!/bin/bash

DEFAULT_SSID="Raspberry Pi AP"
DEFAULT_PASSWORD="raspberry"

if ! cmp -s ~/rpi-long-range-video-transmission/video-transmission/video-transmission.service /etc/systemd/system/video-transmission.service; then
    echo "Copying video transmission service file..."
    sudo cp ~/rpi-long-range-video-transmission/video-transmission/video-transmission.service /etc/systemd/system/

    echo "Reloading systemd daemon..."
    sudo systemctl daemon-reexec
    sudo systemctl daemon-reload

    echo "Enabling video transmission service..."
    sudo systemctl enable video-transmission

    echo "Starting video transmission service..."
    sudo systemctl start video-transmission
else
    echo "Video transmission service already setup and no file changes; skipping"
fi

if ! nmcli connection show | grep -q "YagiAdapter"; then
    echo "Setting up WiFi adapter..."
    sudo nmcli connection add type wifi ifname wlan1 con-name YagiAdapter autoconnect yes ssid $DEFAULT_SSID
    sudo nmcli connection modify YagiAdapter 802-11-wireless.mode ap 802-11-wireless.band bg ipv4.method shared
    sudo nmcli connection modify YagiAdapter wifi-sec.key-mgmt wpa-psk
    sudo nmcli connection modify YagiAdapter wifi-sec.psk $DEFAULT_PASSWORD
    sudo nmcli connection up YagiAdapter
else
    echo "WiFi adapter already setup; skipping"
fi

echo "Done setting up video transmission service!"
