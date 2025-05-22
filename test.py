import subprocess
import re
from luma.core.interface.serial import i2c
from luma.oled.device import sh1106
from PIL import Image, ImageDraw, ImageFont
import keyboard


def scan_wifi():
    try:
        result = subprocess.check_output(["sudo", "iwlist", "wlan0", "scan"]).decode(
            "utf-8"
        )
        ssid_list = re.findall(r'ESSID:"(.*?)"', result)
        # Supprimer les doublons et vides
        ssid_list = list(set([s for s in ssid_list if s]))
        return ssid_list
    except subprocess.CalledProcessError:
        return ["Erreur lors du scan"]


def update_index(event):
    global index, networks, wifiIsSelect
    if event.event_type == "down":
        if event.name == "up":
            index = (index - 1) % len(networks)
        if event.name == "down":
            index = (index + 1) % len(networks)
        if event.name == "enter":
            wifiIsSelect = True


def enter_password(event):
    global password
    if event.event_type == "down":
        password += event.name


# Example d'utilisation
networks = scan_wifi()


serial = i2c(
    port=1, address=0x3C
)  # Address I2C souvent 0x3C, à adapter selon ton i2cdetect
device = sh1106(serial)

# Nettoyer l'écran
device.clear()

# Écrire du texte
font = ImageFont.load_default()

wifiIsSelect = False
index = 0
firstHook = keyboard.hook(update_index)
password = ""

while True:
    if wifiIsSelect:
        keyboard.unhook(firstHook)
        secondHook = keyboard.hook(enter_password)
    image = Image.new("1", (device.width, device.height))
    draw = ImageDraw.Draw(image)
    draw.text((10, 10), networks[index], font=font, fill=255)
    device.display(image)
print("fin du programe")
