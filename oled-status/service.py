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
                    return line.strip().split()[-1]
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
        sha = subprocess.check_output("git rev-parse --short HEAD", shell=True, cwd="/home/pi/oled-status").decode().strip()
        return f"[{sha}]"
    except:
        return ""

def draw_status(lines, sha):
    line_lengths = [len(line) for line in lines]
    min_index = line_lengths.index(min(line_lengths))

    if sha:
        max_chars = WIDTH // 6 
        space_left = max_chars - len(lines[min_index])
        if space_left > len(sha) + 1:
            lines[min_index] += " " * (space_left - len(sha)) + sha

    draw.rectangle((0, 0, WIDTH, HEIGHT), outline=0, fill=0)
    for i, line in enumerate(lines):
        draw.text((0, i * 10), line[:21], font=font, fill=255)
    oled.image(image)
    oled.show()

while True:
    status_lines = []
    for iface in INTERFACES[:HEIGHT // 10]:
        mode = get_mode(iface)
        ssid = get_ssid(iface, mode)

        if mode == "AP":
            clients = get_client_count(iface)
            line = f"{ssid}; {clients} client{'s' if clients != 1 else ''}"
        elif mode == "Client":
            ip = get_ip(iface) or "No IP"
            line = f"{ssid}; {ip}"
        else:
            line = f"{iface}; Unknown"

        status_lines.append(line)

    sha = get_git_short_sha()
    draw_status(status_lines, sha)
    sleep(REFRESH_INTERVAL)
