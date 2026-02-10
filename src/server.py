from api.raspConnection import Connection, create_ports


# le serveur de traitement est sur les port paire
portSensor = create_ports("/tmp/ttyV0", "/tmp/ttyV1")
portActuator = create_ports("/tmp/ttyV2", "/tmp/ttyV3")
portAI = create_ports("/tmp/ttyV4", "/tmp/ttyV5")
portSL = create_ports("/tmp/ttyV6", "/tmp/ttyV7")

connectionSensor = Connection("/tmp/ttyV0", "server -> sensor")
connectionActuator = Connection("/tmp/ttyV2", "server -> actuator")
connectionAI = Connection("/tmp/ttyV4", "server -> AI")
connectionSL = Connection("/tmp/ttyV6", "server -> SL")

mode = "followed by line"


@connectionSensor.on("lineSensor")
def line_sensor(data):
    connectionSL.send("lineSensor", data)


@connectionSensor.on("colorSensor")
def color_sensor(data):
    global mode

    color = data["color"]

    if int(color[:2]) < 160 and int(color[2:4]) > 240 and int(color[4:]) < 160:
        connectionSL.send("interrupt", f'greenSquare{data["side"]}')

    if int(color[:2]) < 160 and int(color[2:4]) > 240 and int(color[4:]) < 160:
        mode = "ball collection"


@connectionSensor.on("distanceSensor")
def distance_sensor(data):
    distance = data["distance"]

    if distance < 20:
        connectionSL.send("interrupt", "objectJustInFront")


@connectionSL.on("motor")
def motor_sl(data):
    if mode == "followed by line":
        connectionActuator.send("motor", data)


@connectionSL.on("motorWhile")
def motor_while_sl(data):
    if mode == "followed by line":
        connectionActuator.send("motorWhile", data)


@connectionAI.on("motor")
def motor_ai(data):
    if mode == "ball collection":
        connectionActuator.send("motor", data)


@connectionAI.on("motorWhile")
def motor_while_ai(data):
    if mode == "ball collection":
        connectionActuator.send("motorWhile", data)


@connectionAI.on("servoMotor")
def servo_motor(data):
    if mode == "ball collection":
        connectionActuator.send("servoMotor", data)


def main():
    try:
        connectionSensor.start()
        connectionActuator.start()
        connectionAI.start()
        connectionSL.start()

    except KeyboardInterrupt:
        connectionSensor.stop(0)
        connectionActuator.stop(0)
        connectionAI.stop(0)
        connectionSL.stop(0)

        portSensor.kill()
        portActuator.kill()
        portAI.kill()
        portSL.kill()

    except Exception as e:
        connectionSensor.stop(2)
        connectionActuator.stop(2)
        connectionAI.stop(2)
        connectionSL.stop(2)

        portSensor.kill()
        portActuator.kill()
        portAI.kill()
        portSL.kill()

        raise e
