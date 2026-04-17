from AlphabotServoMotors import ServoMotors

servo_pince = ServoMotors(22, 50)
servo_levage = ServoMotors(27, 50)

servo_pince.start()
servo_levage.start()

servo_pince.go_to(100)
servo_levage.go_to(175)

servo_pince.go_to(0)
servo_levage.go_to(0)

servo_pince.stop()
servo_levage.stop()
