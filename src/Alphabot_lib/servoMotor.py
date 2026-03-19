# Libraries
import RPi.GPIO as GPIO


class servo_motor:
    def __init__(self):
        GPIO.setmode(GPIO.BOARD)  # Use Board numerotation mode
        GPIO.setwarnings(False)  # Disable warnings

        # Use pin 12 for PWM signal
        pwm_gpio = 7
        frequency = 50
        GPIO.setup(pwm_gpio, GPIO.OUT)
        self.pwm = GPIO.PWM(pwm_gpio, frequency)

    # Set function to calculate percent from angle
    def angle_to_percent(self, angle):
        if angle > 180 or angle < 0:
            return False

        start = 4
        end = 12.5
        ratio = (end - start) / 180  # Calcul ratio from angle to percent

        angle_as_percent = angle * ratio

        return start + angle_as_percent

    def set_angle(self, angle):
        self.pwm.start(self.angle_to_percent(angle))
