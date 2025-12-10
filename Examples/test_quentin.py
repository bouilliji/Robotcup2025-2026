import time
from grove.factory import Factory

# Créez l'objet servomoteur sur le port D5 (peut être D6, D7, etc.)
# Assurez-vous que le port numérique est libre.
# Le numéro du port est le second argument.
servo_pin = 5
servo = Factory.getServo(servo_pin)


# Function pour régler l'angle du servomoteur
def set_angle(angle):
    if angle < 0:
        angle = 0
    elif angle > 180:
        angle = 180

    # La function setAngle() de la librairie gère directement l'angle en degrés
    # Pas besoin de faire la conversion en rapport cyclique (Duty Cycle)
    servo.setAngle(angle)
    time.sleep(0.5)


# Boucle principale
try:
    print("Démarrage du servomoteur via Grove Hat. Appuyez sur Ctrl+C pour quitter.")

    while True:
        print("Position à 0 degrés...")
        set_angle(0)
        time.sleep(1)

        print("Position à 90 degrés...")
        set_angle(90)
        time.sleep(1)

        print("Position à 180 degrés...")
        set_angle(180)
        time.sleep(1)

except KeyboardInterrupt:
    print("\nArrêt du programme.")
    # Le nettoyage est géré automatiquement par la librairie
    # ou vous pouvez explicitement appeler une méthode de nettoyage si disponible
    pass
