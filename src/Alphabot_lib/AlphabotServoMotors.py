# Set function to calculate percent from angle
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)  # Use Board numerotation mode
GPIO.setwarnings(False)


def angle_to_percent(angle):
    if angle > 180 or angle < 0:
        return False

    start = 4
    end = 12.5
    ratio = (end - start) / 180  # Calcul ratio from angle to percent

    angle_as_percent = angle * ratio

    return start + angle_as_percent


class ServoMotors:
    def __init__(self, pin: int, frequency: int):
        GPIO.setup(pin, GPIO.OUT)
        self.pwm = GPIO.PWM(pin, frequency)

    def start(self, angle: int):
        self.pwm.start(angle_to_percent(angle))
        time.sleep(1)

    def go_to(self, angle: int):
        self.pwm.ChangeDutyCycle(angle_to_percent(angle))

    def stop(self):
        self.pwm.stop()
        GPIO.cleanup()
