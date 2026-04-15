# Set function to calculate percent from angle
import RPi.GPIO as GPIO
import time
from enum import Enum

GPIO.setmode(GPIO.BCM)  # Use Board numerotation mode
GPIO.setwarnings(False)


def angle_to_percent_big(angle):
    if angle > 180 or angle < 0:
        return False

    start = 2
    end = 13
    ratio = (end - start) / 180  # Calcul ratio from angle to percent

    angle_as_percent = angle * ratio

    return start + angle_as_percent


def angle_to_percent_small(angle):
    if angle > 180 or angle < 0:
        return False

    start = 2
    end = 12.5
    ratio = (end - start) / 180  # Calcul ratio from angle to percent

    angle_as_percent = angle * ratio

    return start + angle_as_percent


class ServoType(Enum):
    SMALL = True
    BIG = False


class ServoMotors:
    def __init__(self, pin: int, frequency: int, isSmall: ServoType = ServoType.SMALL):
        GPIO.setup(pin, GPIO.OUT)
        self.pwm = GPIO.PWM(pin, frequency)
        self.convert = (
            angle_to_percent_small
            if isSmall == ServoType.SMALL
            else angle_to_percent_big
        )

    def start(self, angle: int):
        self.pwm.start(self.convert(angle))
        time.sleep(1)

    def go_to(self, angle: int):
        self.pwm.ChangeDutyCycle(self.convert(angle))

    def stop(self):
        self.pwm.stop()
        GPIO.cleanup()
