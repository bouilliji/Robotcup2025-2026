from Alphabot_lib.AlphaBotLineSensor import AlphaBotLineSensor as LineSensor
from Alphabot_lib.AlphaBotMotors import AlphaBotMotors as Motors
import time

LS = LineSensor()
motors = Motors()

if __name__ == "__main__":
    print("Line follow Example")

    for i in range(0, 100):
        time.sleep(0.1)
        LS.calibrate()
        print(i)

    while True:
        time.sleep(0.5)
        position = LS.readCalibrated()
        print(position)
