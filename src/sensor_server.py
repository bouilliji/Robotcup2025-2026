import time
import threading

from Alphabot_lib.AlphaBotLineSensor import AlphaBotLineSensor as LineSensor
from Alphabot_lib.DistanceSensor import DistanceSensor

from api.raspConnection import Connection

connectionProcesing = Connection("/tmp/ttyV1", "sensor -> server")

SL = LineSensor()
DS = DistanceSensor()

for i in range(0, 100):
    time.sleep(0.1)
    SL.calibrate()
    print(i)

thread = None
stop_event = threading.Event()


def refined_SL_values(SL):
    values = SL.readCalibrated()

    refinedValues = []

    for value in values:
        if value > 500.0:
            refinedValues.append(1)

        elif value <= 500.0:
            refinedValues.append(0)

    return refinedValues


def send_SL_value():
    while True:
        SLValues = refined_SL_values(SL)
        connectionProcesing.send("lineSensor", SLValues)
        # connectionProcesing.send("distanceSensor", DS.get_distance())

        time.sleep(0.01)


def main():
    global thread

    try:
        connectionProcesing.start()
    except Exception as e:
        connectionProcesing.stop(2)
        raise e

    thread = threading.Thread(target=send_SL_value)
    thread.start()


def stop():
    stop_event.set()
    if thread:
        thread.join()
    connectionProcesing.stop(0)
