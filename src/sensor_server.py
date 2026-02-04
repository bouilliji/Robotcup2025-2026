import sys
import time
from Alphabot_librairy.AlphaBotLineSensor import AlphaBotLineSensor as LineSensor
from Alphabot_librairy.DistanceSensor import DistanceSensor

sys.path.insert(0, "path to /src/")

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
    while True:
        SLValues = refined_SL_values(SL)
        connectionProcesing.send("lineSensor", SLValues)
        connectionProcesing.send("distanceSensor", DS.get_distance())

        time.Sleep(0.01)