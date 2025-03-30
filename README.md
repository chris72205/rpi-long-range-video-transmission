# rpi-long-range-video-transmission
Resources to transmit/receive video from a Raspberry Pi Zero W 2 via a Yagi antenna

The services below assume that you have cloned this repo to the Raspberry Pi at `~/rpi-long-range-video-transmission` and ran `./setup.sh` which installs needed packages system wide.

## video-transmission
This is responsible for setting up an AP and running a server which broadcasts images from the video stream. The server is accessible at port 8080 of the device IP.

### Setup
- run `./video-transmission/setup.sh` to establish the services and configure the WiFi adapter (use env vars `DEFAULT_SSID` and `DEFAULT_PASSWORD` to customize SSID and password)
- add the `./update.sh` script to the crontab of the Raspberry Pi, this will ensure it periodically checks for updates when internet is available
- run `update.sh` to ensure everything is up to date
- visit localhost:8080 on the network (local or Raspberry Pi AP) to verify it's working as expected

## oled-status
This is used to power a small OLED display which will supply some basic networking/debugging issues and hopefully aid in debugging any issues without the need to SSH into the Raspberry Pi.

### Setup
- ensure i2c is enabled via the `raspi-config` tool
- run `./oled-status/setup.sh` to setup and enable the systemd service
- verify that the display is showing information
