from Alphabot_lib.AlphaBotMotors import AlphaBotMotors as Motors
from Alphabot_lib.AlphaBotLineSensor import AlphaBotLineSensor as LineSensor

import time

motor = Motors()
SL = LineSensor()

for i in range(0, 100):
    time.sleep(0.1)
    SL.calibrate()
    print(i)
