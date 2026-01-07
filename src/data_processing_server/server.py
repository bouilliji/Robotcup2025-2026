from api.raspConnection import Connection
import asyncio
import json

connectionSensor = Connection("jepasencoreleport")
connectionActuator = Connection("jepasencoreleport")
connectionAI = Connection("jepasencoreleport")
connectionSL = Connection("jepasencoreleport")

mode = 'followed by line'

@connectionSensor.on("lineSensor")
async def line_sensor(data):
    await connectionSL.send("lineSensor", data)

@connectionSensor.on("colorSensor")
async def color_sensor(data):
    data = json.loads(data)
    color = data["color"]

    if int(color[:2]) < 160 and int(color[2:4]) > 240 and int(color[4:]) < 160:
        await connectionSL.send('interupt', json.dumps({'interuptionType' : f'greenSquare{data["side"]}'}))

    if int(color[:2]) < 160 and int(color[2:4]) > 240 and int(color[4:]) < 160:
        mode = 'ball collection'

@connectionSensor.on("distanceSensor")
async def distance_sensor(data):
    data = json.loads(data)
    distance = data["distance"]

    if distance < 20:
        await connectionSL.send('interupt', json.dumps({'interuptionType' : 'objectJustInFront'}))


@connectionSL.on('motor')
async def motor(data):
    if mode == 'followed by line':
        await connectionActuator.send("motor", data)

@connectionSL.on('motorWhile')
async def motor_while(data):
    if mode == 'followed by line':
        await connectionActuator.send("motorWhile", data)

@connectionAI.on('motor')
async def motor(data):
    if mode == 'ball collection':
        await connectionActuator.send("motor", data)

@connectionAI.on('motorWhile')
async def motor_while(data):
    if mode == 'ball collection':
        await connectionActuator.send("motorWhile", data)

@connectionAI.on('servoMotor')
async def servo_motor(data):
    if mode == 'ball collection':
        await connectionActuator.send("servoMotor", data)

    
async def main():
    try:

        await asyncio.gather(
            connectionSensor.start(),
            connectionActuator.start(),
            connectionAI.start(),
            connectionSL.start(),
        )

    except KeyboardInterrupt:

        await asyncio.gather(
            connectionSensor.stop(0),
            connectionActuator.stop(0),
            connectionAI.stop(0),
            connectionSL.stop(0),
        )

    except Exception as e:

        await asyncio.gather(
            connectionSensor.stop(2),
            connectionActuator.stop(2),
            connectionAI.stop(2),
            connectionSL.stop(2),
        )

        raise e
    

if __name__ == "__main__":
    asyncio.run(main())
