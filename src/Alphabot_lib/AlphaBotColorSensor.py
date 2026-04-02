import board
import adafruit_tcs34725


class ColorSensor:
    def __init__(self):
        i2c = board.I2C()
        self.sensor = adafruit_tcs34725.TCS34725(i2c)

    def isWhite(self):
        return self.sensor.lux > 3000 and min(self.sensor.color_raw) > 15

    def isGreen(self):
        return (
            1500 > self.sensor.lux > 500
            and max(self.sensor.color_raw[:-1]) == self.sensor.color_raw[1]
        )

    def isRed(self):
        return (
            1500 > self.sensor.lux > 500
            and max(self.sensor.color_raw[:-1]) == self.sensor.color_raw[0]
        )

    def isBlack(self):
        return 500 > self.sensor.lux and max(self.sensor.color_raw[:-1]) < 5
