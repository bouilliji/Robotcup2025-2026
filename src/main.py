### Imports ###
# Alphabot library
from Alphabot_lib.AlphaBotLineSensor import AlphaBotLineSensor as LineSensor
from Alphabot_lib.AlphaBotMotors import AlphaBotMotors as Motors
from Alphabot_lib.AlphabotServoMotors import ServoMotors
from Alphabot_lib.AlphaBotColorSensor import ColorSensor
from Alphabot_lib.AlphaBotCamera import Camera

# Sensors
from adafruit_tca9548a import TCA9548A
import board
import busio

# # Object Detection
from ultralytics import YOLO
import cv2

# General
from utils import sign, refined_SL_values
import threading
import time
import argparse
######

### Initialize sensors and actuator ###
# Initialize I2C and TCA9548A multiplexer
i2c = busio.I2C(board.SCL, board.SDA)
tca = TCA9548A(i2c)

# Initialize TCS34725 color sensors
color_sensor_left = ColorSensor(tca[0])
time.sleep(0.1)
color_sensor_right = ColorSensor(tca[1])

# Initialize VL53L0X optical sensor
# optical_sensor = adafruit_vl53l0x.VL53L0X(tca[2])

# Initialize line sensor
SL = LineSensor()


class Robot:
    """
    Class to make the robot follow a line or catch a ball

    Attributes
    ----------
    model_path: str
        path to the yolo model to detect the balls

    Methods
    ----------
    update_line_sensor()
        update the value of the line sensor
    u_turn()
        do a U-Turn
    ninety_turn(direction: int)
        do a 90° turn in a specific direction
    color_sensor_actions()
        actions to do from what color sensors see
    dodge_obstacle()
        to dodge a detected obstacle
    pid()
        calculate the speed of the motors with pid
    modification_v_k(new_error: float, old_error: float)
        modify speed coefficient based on environment (straight line, curve...)
    motor()
        set speed to the motors
    main()
        main action of the robot
    stop()
        stop the servo motors carefully
    """

    def __init__(self, mode="arena"):
        """
        Parameters
        ----------
        model_path: str
            path to the yolo model to detect the balls
        """
        self.model = YOLO(r"/home/athena/dev/Robotcup2025-2026/src/last.onnx")

        self.cam = Camera()

        # Initialize motors
        self.motor = Motors()

        # Initialize camera
        # self.picam = Camera()

        # Initialize servo motors
        self.servo_pliers = ServoMotors(22, 50)
        self.servo_raising = ServoMotors(27, 100)
        ######

        # self.model = YOLO(model_path)  # initialize model

        self.mode = (
            mode  # Set mode at start || arena : to catch ball | line : to follow a line
        )
        self.arene_init_var = False  # init for the arene

        self.state_grab = True

        ### Initialize PID variables ###
        # Sensor values
        self.c1 = 0
        self.c2 = 0
        self.c3 = 0
        self.c4 = 0
        self.c5 = 0

        # Error
        self.error = 0
        self.last_error = 0

        # PID values
        self.p = 0
        self.i = 0
        self.d = 0

        # PID coefficicents
        self.kp = 17
        self.ki = 0.05
        self.kd = 8

        # Speed variables and coefficients
        self.v_d = 0
        self.v_g = 0
        self.v_max = 100
        self.v_min = -100
        self.v_viser = 30
        self.v_curve = 0
        self.v_straight = 0
        ######

        self.thread = None
        self.stop_event = threading.Event()

        # Set servo motors to basic position
        self.servo_pliers.start(100)
        # self.servo_raising.start(175)

        # Start camera
        # self.picam.start()

        self.frame = cv2.imread("img.png")

        self.counter = 0

        self.has_ball = False

        # analyse = threading.Thread(target=self.thread, daemon=True)
        # analyse.start()

    def update_line_sensor(self):
        """Update the value of the line sensor."""

        SLValues = refined_SL_values(SL)  # get refined line sensor's value

        self.c1 = SLValues[0]
        self.c2 = SLValues[1]
        self.c3 = SLValues[2]
        self.c4 = SLValues[3]
        self.c5 = SLValues[4]

    def u_turn(self):
        """Do a U-Turn (180°)."""

        print("do u turn")

        turn_speed = 50
        turn_time = 0.86  # need to be adjusted there

        # Rotate in place (example: left turn)
        self.motor.setMotor(-turn_speed, turn_speed)
        time.sleep(turn_time)

        # Stop after turn
        self.motor.setMotor(0, 0)

    def ninety_turn(self, direction: int):
        """Do a 90° turn in a specific direction.

        Parameters
        ----------
        direction: int
            direction where to do the turn; -1 : left | 1 : right
        """

        print("do a 90° turn in " + str(direction))

        turn_speed = 50
        turn_time1 = 0.51  # left
        turn_time2 = 0.45  # right

        if direction == -1:
            # LEFT turn
            self.motor.setMotor(-turn_speed, turn_speed)
        elif direction == 1:
            # RIGHT turn
            self.motor.setMotor(turn_speed, -turn_speed)

        time.sleep(turn_time1 if direction == -1 else turn_time2)

        # Stop after turn
        self.motor.setMotor(0, 0)

    def color_sensor_actions(self):
        """Actions to do from what color sensors see."""

        if color_sensor_left.isGreen() and color_sensor_right.isGreen():
            self.u_turn()
        elif color_sensor_left.isGreen():
            self.ninety_turn(-1)
        elif color_sensor_right.isGreen():
            self.ninety_turn(1)
        elif color_sensor_left.isRed() or color_sensor_right.isRed():
            self.mode = "arena"

    def dodge_obstacle(self):
        """Dodge a detected obstacle."""

    def pid(self):
        """Calculate the speed of the motors with pid"""

        self.update_line_sensor()  # update line sensor's values

        sum_sensors = (
            self.c1 + self.c2 + self.c3 + self.c4 + self.c5
        )  # sum of sensor's values
        val_sensors = (
            (self.c1 * 4.5) + self.c2 - self.c4 - (self.c5 * 4.5)
        )  # sum with coefficients based on distance from center

        self.error = (
            val_sensors / sum_sensors if sum_sensors > 0 else 0
        )  # distance from line (average the data from the sensor)

        # set pid values
        self.p = self.error
        self.i += self.error
        self.d = self.error - self.last_error

        self.last_error = self.error

        # calculate speed coefficient
        self.modification_v_k(self.error, self.last_error)

        coef = (
            self.kp * self.p + self.ki * self.i + self.kd * self.d
        )  # coefficient from pid

        # speed for right and left motor
        self.v_d = self.v_viser + coef + self.v_straight + self.v_curve
        self.v_g = self.v_viser - coef + self.v_straight + self.v_curve

        self.v_d = min(max(self.v_d, self.v_min), self.v_max)
        self.v_g = min(max(self.v_g, self.v_min), self.v_max)

    def modification_v_k(self, new_error: float, old_error: float):
        """Modify speed coefficient based on environment (straight line, curve...)."""

        if new_error == 0 or sign(new_error) != sign(old_error):
            self.i = 0
            self.v_curve = 0

        if new_error == 0:
            self.v_straight += 0.4
        else:
            self.v_straight = 0
            self.v_curve += 0.1

    def init_motor(self):
        """Set speed to the motors."""

        self.motor.setMotor(self.v_g, self.v_d)

    def arene_init(self):
        print("arene init")
        self.motor.setMotor(0, 0)
        # self.slow_servo(self.servo_raising, 3, 100, 175, 0)
        self.servo_raising.go_to(100)
        self.grab(False)

    def slow_servo(self, servo, t, prec, pos_ini, pos_cib):
        # not instant servo turn (temps,nombre d'étape,position initial, position visée)
        for i in range(prec):
            servo.go_to(pos_ini - ((pos_ini - pos_cib) / prec) * i)
            time.sleep(t / prec)

    def grab(self, state):
        # grab de la pince
        if state:
            self.servo_pliers.go_to(100)
            self.state_grab = True

        else:
            self.servo_pliers.go_to(0)
            self.state_grab = False

    def recherche_ball(self):
        while True:
            self.motor.setMotor(0, -40)
            time.sleep(0.35)
            self.motor.setMotor(0, 0)
            res = self.analyse_yolo()
            ob = self.read_result(res)
            if len(ob) > 0:
                return

    def test(self):
        self.grab(not self.state_grab)

    def analyse_yolo(self):
        # cam.capture_image()
        pict = self.cam.frame()  # get PIL image
        # self.cam.save() # save cam content
        results = self.model.predict(pict, verbose=False, conf=0.5)

        # frame = results[0].plot()

        # cv2.imwrite("img.png",frame)
        # pict.save("img.jpg")
        detected_objects = self.read_result(results)
        return detected_objects

    def dist_milieu(self, x1, x2):
        mid = (x1 + x2) / 2
        return mid - 320

    def read_result(self, results):
        objects = []
        result = results[0]

        for i, box in enumerate(result.boxes):
            cls_id = int(box.cls)
            # label = self.model.names[cls_id]
            # conf = float(box.conf)
            x1, y1, x2, y2 = box.xyxy[0].tolist()

            if cls_id == 0:
                objects.insert(
                    0,
                    {
                        "width": abs(y2 - y1),
                        "mid_dist": self.dist_milieu(x1, x2),
                        "lab": True,
                    },
                )
            else:
                objects.append(
                    {
                        "width": abs(y2 - y1),
                        "mid_dist": self.dist_milieu(x1, x2),
                        "lab": False,
                    }
                )
        return objects

    def grab_ball(self):
        while True:
            res = self.analyse_yolo()
            balls = self.read_result(res)

            if len(balls) > 0:
                ball = balls[0]
                mid = ball["mid_dist"]
                width = ball["width"]
                label = ball["lab"]

                m = min(abs(mid), 100) * 0.01
                if mid > 30:
                    self.motor.setMotor(0, -40)
                    time.sleep(0.15 * m)
                    self.motor.setMotor(0, 0)
                    print("go right")

                elif mid < -30:
                    self.motor.setMotor(-40, 0)
                    time.sleep(0.15 * m)
                    self.motor.setMotor(0, 0)
                    print("go left")

                else:
                    print("go forward")
                    if width < 140:
                        self.motor.setMotor(-40, -40)
                        time.sleep(0.2)
                        self.motor.setMotor(0, 0)
                    else:
                        self.lock_in_ball()
                        return label

            else:
                self.motor.setMotor(0, 0)

    def deliver_ball(self, ball_alive):
        pass

    def lock_in_ball(self):
        self.motor.setMotor(-40, -40)
        time.sleep(0.5)
        self.motor.setMotor(0, 0)

        self.grab(True)

        self.has_ball = True

    def main(self):
        """Main action of the robot."""

        while True:
            if self.mode == "line":
                self.color_sensor_actions()
                self.pid()
                self.init_motor()
                # self.ninety_turn(1)
                # time.sleep(1)
                # self.ninety_turn(-1)
                # break
            elif self.mode == "arena":
                if not self.arene_init_var:
                    self.arene_init()
                    self.arene_init_var = True

                self.recherche_ball()
                label = self.grab_ball()
                self.deliver_ball(label)

    def stop(self):
        """Stop the servo motors carefully."""

        self.motor.setMotor(0, 0)
        self.servo_pliers.stop()
        self.servo_raising.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--mode",
        choices=["line", "arena"],
        default="arena",
        help="Mode de fonctionnement du robot",
    )

    args = parser.parse_args()
    robot = Robot(mode=args.mode)

    try:
        print(f"Mode sélectionné : {args.mode}")
        robot.main()
    except KeyboardInterrupt:
        robot.stop()
