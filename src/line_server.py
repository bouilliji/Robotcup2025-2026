import threading
from api.raspConnection import Connection


def sign(number):
    if number > 0:
        return 1
    elif number < 0:
        return -1
    else:
        return 0


class Robot:
    conn = Connection("/tmp/ttyV7")

    def __init__(self):
        self.conn = Connection("/tmp/ttyV7")
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

    @conn.on("lineSensor")
    def get_capteur(self, data):
        self.c1 = data[0]
        self.c2 = data[1]
        self.c3 = data[2]
        self.c4 = data[3]
        self.c5 = data[4]

    def pid(self):
        capteur_on = self.c2 + self.c3 + self.c4 + self.c5
        val_capteur = self.c2 * 2 + self.c3 - self.c4 - self.c5 * 2
        erreur = val_capteur / capteur_on if capteur_on > 0 else 0

        self.p = erreur
        self.i += erreur
        self.d = erreur - self.last_erreur
        self.last_erreur = erreur

        self.actu_i(self.erreur, self.last_erreur)

        if erreur == 0:
            if self.last_erreur >= self.treeth_turn or self.direc == 1:
                self.v_d = 250
                self.v_g = -250
                self.direc = 1
            elif self.last_erreur <= -self.treeth_turn or self.direc == 2:
                self.v_d = -250
                self.v_g = 250
                self.direc = 2
        else:
            self.aplication_pid()
            self.direc = 0

    def aplication_pid(self):
        coef = self.kp * self.p + self.ki * self.i + self.kd * self.d
        self.v_d = self.v_viser - coef
        self.v_g = self.v_viser + coef

    def actu_i(self, new_erreur, old_erreur):
        if sign(new_erreur) != sign(old_erreur):
            self.i = 0

    def motor(self):
        self.conn.send("motor", {"left": self.v_g, "right": self.v_d})

    def loupe(self):
        while True:
            self.get_capteur()
            self.pid()
            self.motor()

    def main(self):
        thread = threading.Thread(target=self.loupe)
        thread.start()


Rob = Robot()
