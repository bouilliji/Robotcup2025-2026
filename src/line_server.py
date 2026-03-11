import threading
import time
from api.raspConnection import Connection


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


@conn.on("lineSensor")
def get_capteur(data):
    global c1, c2, c3, c4, c5

    c1 = data[0]
    c2 = data[1]
    c3 = data[2]
    c4 = data[3]
    c5 = data[4]


class Robot:
    def __init__(self):
        self.erreur = 0
        self.last_erreur = 0
        self.p = 0
        self.i = 0
        self.d = 0
        self.kp = 110
        self.ki = 0.5
        self.kd = 320
        self.v_d = 0
        self.v_g = 0
        self.direc = 0
        self.new_dir = 0
        self.v_actuelle = 0
        self.v_viser = 200
        self.treeth_turn = 1.5

    def pid(self):
        somme_capteurs = c1 + c2 + c3 + c4 + c5

        if somme_capteurs > 0:
            val_capteur = (c1 * 2) + c2 - c4 - (c5 * 2)

            self.erreur = val_capteur / somme_capteurs

            self.p = self.erreur
            self.i += self.erreur
            self.d = self.erreur - self.last_erreur
            self.last_erreur = self.erreur
            self.actu_i(self.erreur, self.last_erreur)

            self.aplication_pid()
            self.direc = 0
        else:
            if self.last_erreur >= self.treeth_turn or self.direc == 1:
                self.v_d = 250
                self.v_g = -250
                self.direc = 1
            elif self.last_erreur <= -self.treeth_turn or self.direc == 2:
                self.v_d = -250
                self.v_g = 250
                self.direc = 2

    def aplication_pid(self):
        coef = self.kp * self.p + self.ki * self.i + self.kd * self.d
        self.v_d = self.v_viser - coef
        self.v_g = self.v_viser + coef

    def actu_i(self, new_erreur, old_erreur):
        if sign(new_erreur) != sign(old_erreur):
            self.i = 0

    def motor(self):
        conn.send("motor", {"left": self.v_g, "right": self.v_d})

    def loupe(self):
        while True:
            self.pid()
            self.motor()

            time.sleep(0.01)

    def main(self):
        conn.start()
        thread = threading.Thread(target=self.loupe)
        thread.start()
