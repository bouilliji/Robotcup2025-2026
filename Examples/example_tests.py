import RPi.GPIO as GPIO
from Alphabot_lib.AlphaBotLineSensor import AlphaBotLineSensor as LineSensor
from Alphabot_lib.AlphaBotMotors import AlphaBotMotors as Motors
import time

LS = LineSensor()
motors = Motors()

CS = 5
Clock = 25
Address = 24
DataOut = 23

for i in range(0, 100):
    time.sleep(0.1)
    LS.calibrate()
    print(i)

while True:
    position = LS.readCalibrated()
    print(position)
    time.sleep(0.5)
