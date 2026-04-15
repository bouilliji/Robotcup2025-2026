from Alphabot_lib.AlphabotServoMotors import ServoMotors

servo_raising = ServoMotors(22, 50)
input("1")
servo_raising.start(160)

while True:
    i = int(input("where: "))
    servo_raising.go_to(i)
# while True:

#     time.sleep(1)
#     servo_raising.go_to(100)
