import time
from Alphabot_lib.AlphaBotLineSensor import AlphaBotLineSensor as LineSensor
from Alphabot_lib.DistanceSensor import DistanceSensor

from api.raspConnection import Connection

connectionProcesing = Connection("/tmp/ttyV1")

SL = LineSensor()
DS = DistanceSensor()


def refined_SL_values(SL):
    values = SL.readCalibrated()

    refinedValues = []

    for value in values:
        if value > 500.0:
            refinedValues.append(1)

        elif value <= 500.0:
            refinedValues.append(0)

    return refinedValues


def main():
    try:
        connectionProcesing.start()
    except KeyboardInterrupt:
        connectionProcesing.stop(0)
    except Exception as e:
        connectionProcesing.stop(2)
        raise e

    while True:
        SLValues = refined_SL_values(SL)
        connectionProcesing.send("lineSensor", SLValues)
        # connectionProcesing.send("distanceSensor", DS.get_distance())

        time.sleep(0.01)
