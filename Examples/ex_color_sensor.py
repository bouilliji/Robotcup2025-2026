from adafruit_tca9548a import TCA9548A
import adafruit_tcs34725
import board
import busio
import time

i2c = busio.I2C(board.SCL, board.SDA)
tca = TCA9548A(i2c)

color_l = adafruit_tcs34725.TCS34725(tca[1])
time.sleep(0.1)
color_r = adafruit_tcs34725.TCS34725(tca[0])

color_l.integration_time = 100  # In milliseconds

color_r.integration_time = 100  # In milliseconds

try:
    while True:
        # Read color values
        rgb1 = color_l.color_rgb_bytes

        print(rgb1)

        rgb2 = color_r.color_rgb_bytes

        print(rgb2)
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting...")
