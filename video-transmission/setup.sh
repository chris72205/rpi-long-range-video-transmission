#!/bin/bash

DEFAULT_SSID="LR Video"
DEFAULT_PASSWORD="longrangevideolongrangevideo"

if ! cmp -s ~/rpi-long-range-video-transmission/video-transmission/video-transmission.service /etc/systemd/system/video-transmission.service; then
    echo "Copying video transmission service file...."
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
    sudo nmcli con add type wifi ifname wlan1 mode ap con-name YagiAdapter ssid "$DEFAULT_SSID"
    sudo nmcli con modify YagiAdapter 802-11-wireless.band bg
    sudo nmcli con modify YagiAdapter 802-11-wireless.channel 6
    sudo nmcli con modify YagiAdapter ipv4.method shared
    sudo nmcli con modify YagiAdapter 802-11-wireless-security.key-mgmt wpa-psk
    sudo nmcli con modify YagiAdapter 802-11-wireless-security.proto rsn
    sudo nmcli con modify YagiAdapter 802-11-wireless-security.pairwise ccmp
    sudo nmcli con modify YagiAdapter 802-11-wireless-security.group ccmp
    sudo nmcli con modify YagiAdapter 802-11-wireless-security.pmf disable
    sudo nmcli con modify YagiAdapter 802-11-wireless-security.psk "$DEFAULT_PASSWORD"
    sudo nmcli con up YagiAdapter
else
    echo "WiFi adapter already setup; skipping"
fi

echo "Done setting up video transmission service!"
