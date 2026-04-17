from Alphabot_lib.AlphaBotLineSensor import AlphaBotLineSensor as LineSensor
from Alphabot_lib.AlphaBotMotors import AlphaBotMotors as Motors
from Alphabot_lib.DistanceSensor import DistanceSensor as DS

# from Alphabot_lib.AlphaBotColorSensor import ColorSensor as CS
import time

LS = LineSensor()
motors = Motors()
DistanceSensor = DS()
# cs = CS()

if __name__ == "__main__":
    print("Test distance sensor")

    try:
        # La boucle principale lira la portée et l'affichera chaque seconde.
        while True:
            print("Range: {0}mm".format(DistanceSensor.get_distance()))
            time.sleep(0.11)
    except KeyboardInterrupt:
        print("Exit")  # Sortie sur CTRL+C

    '''while True:
        # print('distance')
        # print(DistanceSensor.get_distance())

        print("""------------------
isWhite: {}
isBlack: {}
isGreen: {}
isRed: {}""".format(cs.isWhite(),cs.isBlack(),cs.isGreen(),cs.isRed()))

        time.sleep(0.1)'''

    """print("Line follow Example")

    for i in range(0, 100):
        time.sleep(0.1)
        LS.calibrate()
        print(i)

    while True:
        time.sleep(0.5)
        position = LS.readCalibrated()
        print(position)"""
