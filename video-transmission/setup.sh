#!/bin/bash

DEFAULT_SSID="Raspberry Pi AP"
DEFAULT_PASSWORD="raspberry"

echo "Copying video transmission service file..."
sudo cp video-transmission.service /etc/systemd/system/

echo "Reloading systemd daemon..."
sudo systemctl daemon-reexec
sudo systemctl daemon-reload

echo "Enabling video transmission service..."
sudo systemctl enable video-transmission

echo "Starting video transmission service..."
sudo systemctl start video-transmission

echo "Setting up WiFi adapter..."
sudo nmcli connection add type wifi ifname wlan1 con-name YagiAdapter autoconnect yes ssid $DEFAULT_SSID
sudo nmcli connection modify YagiAdapter 802-11-wireless.mode ap 802-11-wireless.band bg ipv4.method shared
sudo nmcli connection modify YagiAdapter wifi-sec.key-mgmt wpa-psk
sudo nmcli connection modify YagiAdapter wifi-sec.psk $DEFAULT_PASSWORD
sudo nmcli connection up YagiAdapter

echo "Done!"
