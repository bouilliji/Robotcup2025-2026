import sys

sys.path.insert(0, "path to /src/")

from api.raspConnection import Connection, create_ports


#le serveur de traitement est sur les port paire
portSensor = create_ports("/tmp/ttyV0", "/tmp/ttyV1")
portActuator = create_ports("/tmp/ttyV2", "/tmp/ttyV3")
portAI = create_ports("/tmp/ttyV4", "/tmp/ttyV5")
portSL = create_ports("/tmp/ttyV6", "/tmp/ttyV7")

connectionSensor = Connection("/tmp/ttyV0")
connectionActuator = Connection("/tmp/ttyV2")
connectionAI = Connection("/tmp/ttyV4")
connectionSL = Connection("/tmp/ttyV6")

mode = 'followed by line'

@connectionSensor.on("lineSensor")
def line_sensor(data):
    connectionSL.send("lineSensor", data)

@connectionSensor.on("colorSensor")
def color_sensor(data):
    color = data["color"]

    if int(color[:2]) < 160 and int(color[2:4]) > 240 and int(color[4:]) < 160:
        connectionSL.send('interupt', f'greenSquare{data["side"]}')

    if int(color[:2]) < 160 and int(color[2:4]) > 240 and int(color[4:]) < 160:
        mode = 'ball collection'

@connectionSensor.on("distanceSensor")
def distance_sensor(data):
    distance = data["distance"]

    if distance < 20:
        connectionSL.send('interupt','objectJustInFront')


@connectionSL.on('motor')
def motor(data):
    if mode == 'followed by line':
        connectionActuator.send("motor", data)

@connectionSL.on('motorWhile')
def motor_while(data):
    if mode == 'followed by line':
        connectionActuator.send("motorWhile", data)

@connectionAI.on('motor')
def motor(data):
    if mode == 'ball collection':
        connectionActuator.send("motor", data)

@connectionAI.on('motorWhile')
def motor_while(data):
    if mode == 'ball collection':
        connectionActuator.send("motorWhile", data)

@connectionAI.on('servoMotor')
def servo_motor(data):
    if mode == 'ball collection':
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
    

if __name__ == "__main__":
    main()
