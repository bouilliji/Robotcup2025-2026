import time
import RPi.GPIO as GPIO


class DistanceSensor:

    def __init__(self, trigPin=18, echoPin=23):
        self.echoPin = echoPin
        self.trigPin = trigPin

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.trigPin,GPIO.OUT)
        GPIO.setup(self.echoPin,GPIO.IN)

        GPIO.output(self.trigPin, False)

    def get_distance(self):
        GPIO.output(self.trigPin, True)
        time.sleep(0.00001)
        GPIO.output(self.trigPin, False)

        while GPIO.input(self.echoPin)==0:
            pulse_start = time.time()
        while GPIO.input(self.echoPin)==1:
            pulse_end = time.time()

        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150
        distance = round(distance, 2)

        return distance

