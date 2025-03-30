import subprocess
from time import sleep

import board
import busio
from adafruit_ssd1306 import SSD1306_I2C
from PIL import Image, ImageDraw, ImageFont

# ======= Configuration =======
INTERFACES = ["wlan0", "wlan1"]
REFRESH_INTERVAL = 10  # seconds
# =============================

# OLED config
WIDTH = 128
HEIGHT = 32
i2c = busio.I2C(board.SCL, board.SDA)
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)
font = ImageFont.load_default()

# Drawing canvas
image = Image.new("1", (WIDTH, HEIGHT))
draw = ImageDraw.Draw(image)

def get_mode(iface):
    try:
        out = subprocess.check_output(f"iw dev {iface} info", shell=True).decode()
        if "type AP" in out:
            return "AP"
        elif "type managed" in out:
            return "Client"
        else:
            return "Unknown"
    except:
        return "Unknown"

def get_ip(iface):
    try:
        result = subprocess.check_output(f"ip addr show {iface}", shell=True).decode()
        for line in result.splitlines():
            line = line.strip()
            if line.startswith("inet "):
                return line.split()[1].split("/")[0]
        return None
    except:
        return None

def get_ssid(iface, mode):
    try:
        if mode == "AP":
            out = subprocess.check_output(f"iw dev {iface} info", shell=True).decode()
            for line in out.splitlines():
                if "ssid" in line.lower():
                    return "AP: " +line.strip().split()[-1]
        else:
            out = subprocess.check_output(f"iwgetid {iface} -r", shell=True).decode().strip()
            return out if out else "No SSID"
        return "No SSID"
    except:
        return "No SSID"

def get_client_count(iface):
    try:
        out = subprocess.check_output(f"iw dev {iface} station dump", shell=True).decode()
        clients = [line for line in out.splitlines() if line.startswith("Station")]
        return len(clients)
    except:
        return 0

def get_git_short_sha():
    try:
        sha = subprocess.check_output("git rev-parse --short HEAD", shell=True, cwd="/home/chris/rpi-long-range-video-transmission").decode().strip()
        return f"[{sha}]"
    except Exception as e:
        print(f"Error getting SHA: {e}")
        return "unknown"

def draw_status(lines, sha):
    draw.rectangle((0, 0, WIDTH, HEIGHT), outline=0, fill=0)
    for i, line in enumerate(lines):
        draw.text((0, i * 10), line[:21], font=font, fill=255)

    if sha:
        # Estimate right-aligned x-position
        text_width = len(sha) * 6  # ~6px per char in default font
        x_pos = WIDTH - text_width
        draw.text((x_pos, HEIGHT - 10), sha, font=font, fill=255)
    else:
        draw.text((0, HEIGHT - 10), "No SHA", font=font, fill=255)

    oled.image(image)
    oled.show()

while True:
    status_lines = []
    for iface in INTERFACES[:2]:  # Only room for 2 lines
        mode = get_mode(iface)
        ssid = get_ssid(iface, mode)

        if mode == "AP":
            clients = get_client_count(iface)
            line = f"{ssid} {clients}"
        elif mode == "Client":
            ip = get_ip(iface) or "No IP"
            line = f"{ssid}; {ip}"
        else:
            line = f"{iface}; Unknown"

        status_lines.append(line)

    sha = get_git_short_sha()
    draw_status(status_lines, sha)
    sleep(REFRESH_INTERVAL)
