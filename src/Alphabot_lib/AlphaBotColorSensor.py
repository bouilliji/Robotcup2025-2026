import adafruit_tcs34725


class ColorSensor:
    def __init__(self, channel):
        self.sensor = adafruit_tcs34725.TCS34725(channel)

    def isWhite(self):
        return self.sensor.lux > 3000 and min(self.sensor.color_raw) > 15

    def isGreen(self):
        rgb = self.sensor.color_rgb_bytes

        r, g, b = rgb

        return g > 26

    def isRed(self):
        rgb = self.sensor.color_rgb_bytes

        r, g, b = rgb

        return r > 26

    def isBlack(self):
        return 500 > self.sensor.lux and max(self.sensor.color_raw[:-1]) < 5

    def all(self):
        return (round(self.sensor.lux), self.sensor.color_raw[:-1])

    def calibrate(self):
        print("GIME THE RED")
        input()
