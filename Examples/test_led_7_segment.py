import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.OUT)

while True:
    try:
        GPIO.output(12, GPIO.HIGH)
    except:
        print("fin du programme")
        break

GPIO.output(12, GPIO.LOW)
