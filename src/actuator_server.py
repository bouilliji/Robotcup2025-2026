import time
from Alphabot_lib.AlphaBotMotors import AlphaBotMotors as Motors

from api.raspConnection import Connection

connectionProcesing = Connection("/tmp/ttyV3", "actuator -> server")

motor = Motors()


@connectionProcesing.on("motor")
def motor_process(data):
    motor.setMotor(data["left"], data["right"])


@connectionProcesing.on("motorWhile")
def motor_while_process(data):
    motor.setMotor(data["left"], data["right"])
    time.sleep(data["time"])
    motor.setMotor(0, 0)
    motor.stop()


def main():
    try:
        connectionProcesing.start()

    except KeyboardInterrupt:
        connectionProcesing.stop(0)
        motor.stop()

    except Exception as e:
        connectionProcesing.stop(2)
        motor.stop()
        raise e
