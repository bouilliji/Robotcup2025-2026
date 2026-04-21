### Imports ###
# Alphabot library
from Alphabot_lib.AlphaBotLineSensor import AlphaBotLineSensor as LineSensor
from Alphabot_lib.AlphaBotMotors import AlphaBotMotors as Motors
from Alphabot_lib.AlphabotServoMotors import ServoMotors, ServoType
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
import threading
import time
import argparse
from line_following import *
from arena_mode import *
######

### Initialize sensors and actuator ###
# Initialize I2C and TCA9548A multiplexer
i2c = busio.I2C(board.SCL, board.SDA)
tca = TCA9548A(i2c)


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

        # Initialize motors
        self.motor = Motors()

        # Initialize camera
        self.cam = Camera()

        # Initialize servo motors
        self.servo_pliers = ServoMotors(27, 50, ServoType.SMALL)
        self.servo_raising = ServoMotors(22, 50, ServoType.BIG)
        ######

        # Initialize TCS34725 color sensors
        self.color_l = ColorSensor(tca[0])
        time.sleep(0.1)
        self.color_r = ColorSensor(tca[1])

        self.color_l.sensor.integration_time = 100  # In milliseconds
        self.color_r.sensor.integration_time = 100  # In milliseconds

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
        self.v_viser = 15
        self.v_curve = 0
        self.v_straight = 0
        ######

        self.thread = None
        self.stop_event = threading.Event()

        # Set servo motors to basic position
        self.servo_pliers.start(0)
        self.servo_raising.start(0)

        self.counter = 0

    def main(self):
        """Main action of the robot."""

        while True:
            if self.mode == "line":
                color_sensor_actions()
                pid()
                init_motor()
                # self.ninety_turn(1)
                # time.sleep(1)
                # self.ninety_turn(-1)
                # break
            elif self.mode == "arena":
                print(self.mode)
                if not self.arene_init_var:
                    arene_init()
                    self.arene_init_var = True

                # self.test()

                recherche_ball()
                label = grab_ball()
                time.sleep(1)
                raisearm(True)

                deliver_ball(label)

    def stop(self):
        """Stop the servo motors carefully."""

        self.motor.setMotor(0, 0)
        self.servo_pliers.stop()
        self.servo_raising.stop()

    def zgueg(self):
        """ntm ta mere la pute"""

        self.motor.setMotor(300,-300)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--mode",
        choices=["line", "arena"],
        default="line",
        help="Mode de fonctionnement du robot",
    )

    args = parser.parse_args()
    robot = Robot(mode=args.mode)

    try:
        print(f"Mode sélectionné : {args.mode}")
        robot.main()
    except KeyboardInterrupt:
        robot.stop()
