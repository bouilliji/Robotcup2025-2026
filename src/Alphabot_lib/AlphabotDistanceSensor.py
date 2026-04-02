import board
import busio
import adafruit_vl53l0x


class DistanceSensor:
    def __init__(self):
        i2c = busio.I2C(board.SCL, board.SDA)
        self.vl53 = adafruit_vl53l0x.VL53L0X(i2c)

    def get_distance(self):
        return self.vl53.range
