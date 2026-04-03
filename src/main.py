### Imports ###
# Alphabot library
from Alphabot_lib.AlphaBotLineSensor import AlphaBotLineSensor as LineSensor
from Alphabot_lib.AlphaBotMotors import AlphaBotMotors as Motors
from Alphabot_lib.AlphabotServoMotors import ServoMotors
from Alphabot_lib.AlphaBotColorSensor import ColorSensor

# Sensors
from adafruit_tca9548a import TCA9548A
import adafruit_vl53l0x
import board
import busio

# Object Detection
from ultralytics import YOLO

# General
from utils import sign, refined_SL_values
import threading
import time
######

### Initialize sensors and actuator ###
# Initialize I2C and TCA9548A multiplexer
i2c = busio.I2C(board.SCL, board.SDA)
tca = TCA9548A(i2c)

# Initialize TCS34725 color sensors
color_sensor_left = ColorSensor(tca[0])
color_sensor_right = ColorSensor(tca[1])

# Initialize VL53L0X optical sensor
optical_sensor = adafruit_vl53l0x.VL53L0X(tca[2])

# Initialize line sensor
SL = LineSensor()

# Initialize motors
motor = Motors()

# Initialize servo motors
servo_pliers = ServoMotors(22, 50)
servo_raising = ServoMotors(27, 50)
######

### Variables ###
model_path = "path to model"
######


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

    def __init__(self, model_path: str):
        """
        Parameters
        ----------
        model_path: str
            path to the yolo model to detect the balls
        """

        self.model = YOLO(model_path)  # initialize model

        self.mode = "line"  # Set mode at start || arena : to catch ball | line : to follow a line

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
        servo_pliers.start(100)
        servo_raising.start(175)

    def update_line_sensor(self):
        """Update the value of the line sensor."""

        SLValues = refined_SL_values(SL)  # get refined line sensor's value

        self.c1 = SLValues[0]
        self.c2 = SLValues[1]
        self.c3 = SLValues[2]
        self.c4 = SLValues[3]
        self.c5 = SLValues[4]

    def u_turn(self):
        """Do a U-Turn."""

        print("do u turn")

    def ninety_turn(self, direction: int):
        """Do a 90° turn in a specific direction.

        Parameters
        ----------
        direction: int
            direction where to do the turn; -1 : left | 1 : right
        """

        print("do a 90° turn in " + str(direction))

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

        # write dodge obstacle
        print("dodge obstacle")

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

    def motor(self):
        """Set speed to the motors."""

        motor.setMotor(self.v_g, self.v_d)

    def main(self):
        """Main action of the robot."""

        while True:
            if self.mode == "line":
                self.color_sensor_actions()
                self.pid()
                self.motor()
                time.sleep(0.01)
            elif self.mode == "arena":
                # mode arène
                print("mode arène")

    def stop(self):
        """Stop the servo motors carefully."""

        servo_pliers.stop()
        servo_raising.stop()


if __name__ == "__main__":
    robot = Robot(model_path)

    try:
        robot.main()
    except KeyboardInterrupt:
        robot.stop()
