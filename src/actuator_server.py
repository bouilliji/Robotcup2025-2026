import sys
import time
from Alphabot_librairy.AlphaBotMotors import AlphaBotMotors as Motors

sys.path.insert(0, "path to /src/")

from api.raspConnection import Connection

connectionProcesing = Connection("/tmp/ttyV3")

motor = Motors()

@connectionProcesing.on('motor')
def motor(data):
    motor.setMotor(data['left'], data['right'])

@connectionProcesing.on('motorWhile')
def motorWhile(data):
    motor.setMotor(data['left'], data['right'])
    time.sleep(data['time'])
    motor.stop()