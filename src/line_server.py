from re import error
import threading
import time
from api.raspConnection import Connection

from Alphabot_lib.AlphaBotMotors import AlphaBotMotors as Motors
from Alphabot_lib.AlphaBotLineSensor import AlphaBotLineSensor as LineSensor

motor = Motors()
SL = LineSensor()


def sign(number):
    if number > 0:
        return 1
    elif number < 0:
        return -1
    else:
        return 0


conn = Connection("/tmp/ttyV7", "SL -> server")

c1 = 0
c2 = 0
c3 = 0
c4 = 0
c5 = 0


def refined_SL_values(SL):
    values = SL.readCalibrated()

    refinedValues = []

    for value in values:
        if value > 500.0:
            refinedValues.append(1)

        elif value <= 500.0:
            refinedValues.append(0)

    return refinedValues


def get_capteur():
    global c1, c2, c3, c4, c5

    SLValues = refined_SL_values(SL)

    c1 = SLValues[0]
    c2 = SLValues[1]
    c3 = SLValues[2]
    c4 = SLValues[3]
    c5 = SLValues[4]


class Robot:
    def __init__(self):
        self.erreur = 0
        self.last_erreur = 0

        self.p = 0
        self.i = 0
        self.d = 0

        self.kp = 17
        self.ki = 0.0001
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

    def pid(self):
        somme_capteurs = c1 + c2 + c3 + c4 + c5

        val_capteur = (c1 * 4.5) + c2 - c4 - (c5 * 4.5)

        self.erreur = val_capteur / somme_capteurs if somme_capteurs > 0 else 0

        self.p = self.erreur
        self.i += self.erreur
        self.d = self.erreur - self.last_erreur
        self.last_erreur = self.erreur

        self.modification_v_k(self.erreur, self.last_erreur)

        print(self.v_g, self.v_d)

        self.aplication_pid()

    def aplication_pid(self):
        coef = self.kp * self.p + self.ki * self.i + self.kd * self.d
        self.v_d = self.v_viser + coef + self.v_line_droite + self.v_courbe
        self.v_g = self.v_viser - coef + self.v_line_droite + self.v_courbe

        self.v_d = min(max(self.v_d, self.v_min), self.v_max)
        self.v_g = min(max(self.v_g, self.v_min), self.v_max)

    def modification_v_k(self, new_erreur, old_erreur):
        if new_erreur == 0 or sign(new_erreur) != sign(old_erreur):
            self.i = 0
            self.v_courbe = 0

        if new_erreur == 0:
            self.v_line_droite += 0.4
        else:
            self.v_line_droite = 0
            self.v_courbe += 0.1

    def actu_v_ligne_d(self):
        if self.v_g == self.v_d:
            self.v_line_droite += 0.4
        else:
            self.v_line_droite = 0

    def motor(self):
        motor.setMotor(self.v_g, self.v_d)

    def loupe(self):
        while True:
            get_capteur()
            self.pid()
            self.motor()
            time.sleep(0.01)

    def main(self):
        conn.start()
        self.thread = threading.Thread(target=self.loupe)
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        if self.thread:
            self.thread.join()
        conn.stop(0)


robot = Robot()

try:
    robot.loupe()
except error:
    pass
