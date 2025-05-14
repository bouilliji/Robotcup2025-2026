# Libraries
import RPi.GPIO as GPIO
import time

# Mode for the pin
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# Pin of the led
LED = 7

GPIO.setup(LED, GPIO.OUT)

state = GPIO.input(LED)

# Led on at a power
while True:
    GPIO.output(LED, GPIO.HIGH)
    time.sleep(0.001)
    GPIO.output(LED, GPIO.LOW)
    time.sleep(0.009)

GPIO.cleanup()
