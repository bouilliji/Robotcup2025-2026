import RPi.GPIO as GPIO
from Alphabot_librairy.AlphaBotLineSensor import AlphaBotLineSensor as LineSensor
from Alphabot_librairy.AlphaBotMotors import AlphaBotMotors as Motors
import time

LS = LineSensor()
motors = Motors()

if __name__ == "__main__":
    time.sleep(10)

    motors.setMotor(100, 100)
    motors.forward()
    time.sleep(2)
    motors.backward()
    time.sleep(2)
    motors.left()
    time.sleep(2)
    motors.right()
    time.sleep(2)
    motors.stop()

    print("Line follow Example")
    time.sleep(0.5)
    for i in range(0, 400):
        LS.calibrate()
        print(i)

    while True:
        time.sleep(0.5)
        position = LS.AnalogRead()
        print(position)
