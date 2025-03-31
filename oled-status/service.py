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

def draw_status(line1, line2, clients, sha):
    draw.rectangle((0, 0, WIDTH, HEIGHT), outline=0, fill=0)

    # Line 1: wlan0 – SSID; IP
    draw.text((0, 0), line1[:21], font=font, fill=255)

    # Line 2: wlan1 – SSID
    draw.text((0, 10), line2[:21], font=font, fill=255)

    # Line 3: left = client count, right = SHA
    client_text = f"{clients} client{'s' if clients != 1 else ''}"
    draw.text((0, 20), client_text, font=font, fill=255)

    if sha:
        sha_width = len(sha) * 6  # estimate width
        draw.text((WIDTH - sha_width, 20), sha, font=font, fill=255)

    oled.image(image)
    oled.show()


while True:
    # --- wlan0 (client) ---
    iface0 = INTERFACES[0]
    mode0 = get_mode(iface0)
    ssid0 = get_ssid(iface0, mode0)
    ip0 = get_ip(iface0) or "No IP"
    line1 = f"{ssid0}; {ip0}" if mode0 == "Client" else f"{iface0}; Unknown"

    # --- wlan1 (AP) ---
    iface1 = INTERFACES[1]
    mode1 = get_mode(iface1)
    ssid1 = get_ssid(iface1, mode1)
    line2 = ssid1 if mode1 == "AP" else f"{iface1}; Unknown"

    # --- Clients + SHA ---
    clients = get_client_count(iface1) if mode1 == "AP" else 0
    sha = get_git_short_sha()

    draw_status(line1, line2, clients, sha)
    sleep(REFRESH_INTERVAL)