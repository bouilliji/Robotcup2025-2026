import threading
import time
# from ultralytics import YOLO
# import cv2

from Alphabot_lib.AlphaBotMotors import AlphaBotMotors as Motors
from Alphabot_lib.AlphaBotLineSensor import AlphaBotLineSensor as LineSensor
from Alphabot_lib.AlphabotServoMotors import ServoMotors
# import adafruit_tcs34725
# import board

# # Initialize I2C and TCS34725 sensor
# i2c = board.I2C()
# sensor = adafruit_tcs34725.TCS34725(i2c)

motor = Motors()
SL = LineSensor()
servo_pince = ServoMotors(22, 50)
servo_levage = ServoMotors(27, 50)


def sign(number):
    if number > 0:
        return 1
    elif number < 0:
        return -1
    else:
        return 0


def refined_SL_values(SL):
    values = SL.readCalibrated()

    refinedValues = []

    for value in values:
        if value > 500.0:
            refinedValues.append(1)

        elif value <= 500.0:
            refinedValues.append(0)

    return refinedValues


class Robot:
    def __init__(self):
        self.mode = "line"
        # self.model = YOLO("path to Model")

        self.c1 = 0
        self.c2 = 0
        self.c3 = 0
        self.c4 = 0
        self.c5 = 0

        self.erreur = 0
        self.last_erreur = 0

        self.p = 0
        self.i = 0
        self.d = 0

        self.kp = 17
        self.ki = 0.05
        self.kd = 8

        self.v_d = 0
        self.v_g = 0
        self.v_max = 100
        self.v_min = -100
        self.v_viser = 30
        self.v_line_droite = 0
        self.v_courbe = 0

        self.thread = None
        self.stop_event = threading.Event()

        servo_pince.start(100)
        servo_levage.start(175)

    def actu_capteur_line(self):
        SLValues = refined_SL_values(SL)

        self.c1 = SLValues[0]
        self.c2 = SLValues[1]
        self.c3 = SLValues[2]
        self.c4 = SLValues[3]
        self.c5 = SLValues[4]

    # def get_capteur_color(self):
    #     isGreen = lambda sensor: 1500 > sensor.lux > 500 and max(sensor.color_raw[:-1])==sensor.color_raw[1]
    #     isRed = lambda sensor: 1500 > sensor.lux > 500 and max(sensor.color_raw[:-1])==sensor.color_raw[0]
    #     isBlack = lambda sensor: 500 > sensor.lux and max(sensor.color_raw[:-1])<5

    #     return isGreen, isRed, isBlack

    def pid(self):
        self.actu_capteur_line()

        somme_capteurs = self.c1 + self.c2 + self.c3 + self.c4 + self.c5
        val_capteur = (self.c1 * 4.5) + self.c2 - self.c4 - (self.c5 * 4.5)

        self.erreur = val_capteur / somme_capteurs if somme_capteurs > 0 else 0

        self.p = self.erreur
        self.i += self.erreur
        self.d = self.erreur - self.last_erreur
        self.last_erreur = self.erreur

        self.modification_v_k(self.erreur, self.last_erreur)

        coef = self.kp * self.p + self.ki * self.i + self.kd * self.d
        self.v_d = self.v_viser + coef + self.v_line_droite + self.v_courbe
        self.v_g = self.v_viser - coef + self.v_line_droite + self.v_courbe

        self.v_d = min(max(self.v_d, self.v_min), self.v_max)
        self.v_g = min(max(self.v_g, self.v_min), self.v_max)

    def dodge_obstacle(self):
        # write dodge obstacle
        print("dodge bro")

    def modification_v_k(self, new_erreur, old_erreur):
        if new_erreur == 0 or sign(new_erreur) != sign(old_erreur):
            self.i = 0
            self.v_courbe = 0

        if new_erreur == 0:
            self.v_line_droite += 0.4
        else:
            self.v_line_droite = 0
            self.v_courbe += 0.1

    def motor(self):
        motor.setMotor(self.v_g, self.v_d)

    def main(self):
        while True:
            if self.mode == "line":
                # isGreen, isRed, isBlack = self.get_capteur_color()
                # if isGreen:
                #     print("turn 90")
                # elif isRed:
                #     mode = "arena"
                # else:
                self.pid()
                self.motor()
                time.sleep(0.01)

            elif self.mode == "arena":
                # mode arène
                print("mode arène")

    def stop(self):
        servo_pince.stop()
        servo_levage.stop()


robot = Robot()

try:
    robot.main()
except KeyboardInterrupt:
    robot.stop()
