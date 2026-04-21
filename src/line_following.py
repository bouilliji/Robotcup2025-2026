import time

from Alphabot_lib.AlphaBotLineSensor import AlphaBotLineSensor as LineSensor
from utils import sign



SL = LineSensor()


def update_line_sensor(robot):
    """Update the value of the line sensor."""

    SLValues = SL.refined_SL_values()  # get refined line sensor's value

    robot.c1 = SLValues[0]
    robot.c2 = SLValues[1]
    robot.c3 = SLValues[2]
    robot.c4 = SLValues[3]
    robot.c5 = SLValues[4]

def u_turn(robot):
    """Do a U-Turn (180°)."""

    print("do u turn")

    turn_speed = 50
    turn_time = 0.86  # need to be adjusted there

    # Rotate in place (example: left turn)
    robot.motor.setMotor(-turn_speed, turn_speed)
    time.sleep(turn_time)

    # Stop after turn
    robot.motor.setMotor(0, 0)

def ninety_turn(robot, direction: int):
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
        robot.motor.setMotor(-turn_speed, turn_speed)
    elif direction == 1:
        # RIGHT turn
        robot.motor.setMotor(turn_speed, -turn_speed)

    time.sleep(turn_time1 if direction == -1 else turn_time2)

    # Stop after turn
    robot.motor.setMotor(0, 0)

def color_sensor_actions(robot):
    """Actions to do from what color sensors see."""

    if robot.color_l.isGreen() and robot.color_r.isGreen():
        print("u turn")
        robot.u_turn()
    elif robot.color_l.isGreen():
        print("turn l")
        robot.ninety_turn(-1)
    elif robot.color_r.isGreen():
        print("turn r")
        robot.ninety_turn(1)
    elif robot.color_l.isRed() or robot.color_r.isRed():
        print("mode arena")
        robot.mode = "arena"

def dodge_obstacle(robot):
    """Dodge a detected obstacle."""
    t = 0.2
    
    robot.ninety_turn(1)
    robot.motor.setMotor(20,20)
    time.sleep(t)
    robot.motor.setMotor(0,0)
    
    robot.ninety_turn(-1)
    robot.motor.setMotor(20,20)
    time.sleep(t)
    robot.motor.setMotor(0,0)
    
    robot.ninety_turn(-1)
    robot.motor.setMotor(20,20)
    time.sleep(t)
    robot.motor.setMotor(0,0)
    
    robot.ninety_turn(1)
    robot.motor.setMotor(20,20)
    time.sleep(t)
    robot.motor.setMotor(0,0)
    
    

def pid(robot):
    """Calculate the speed of the motors with pid"""

    robot.update_line_sensor()  # update line sensor's values

    sum_sensors = (
        robot.c1 + robot.c2 + robot.c3 + robot.c4 + robot.c5
    )  # sum of sensor's values
    val_sensors = (
        (robot.c1 * 4.5) + robot.c2 - robot.c4 - (robot.c5 * 4.5)
    )  # sum with coefficients based on distance from center

    robot.error = (
        val_sensors / sum_sensors if sum_sensors > 0 else 0
    )  # distance from line (average the data from the sensor)

    # set pid values
    robot.p = robot.error
    robot.i += robot.error
    robot.d = robot.error - robot.last_error

    robot.last_error = robot.error

    # calculate speed coefficient
    robot.modification_v_k(robot.error, robot.last_error)

    coef = (
        robot.kp * robot.p + robot.ki * robot.i + robot.kd * robot.d
    )  # coefficient from pid

    # speed for right and left motor
    robot.v_d = robot.v_viser + coef + robot.v_straight + robot.v_curve
    robot.v_g = robot.v_viser - coef + robot.v_straight + robot.v_curve

    robot.v_d = min(max(robot.v_d, robot.v_min), robot.v_max)
    robot.v_g = min(max(robot.v_g, robot.v_min), robot.v_max)

def modification_v_k(robot, new_error: float, old_error: float):
    """Modify speed coefficient based on environment (straight line, curve...)."""

    if new_error == 0 or sign(new_error) != sign(old_error):
        robot.i = 0
        robot.v_curve = 0

    if new_error == 0:
        robot.v_straight += 0.4
    else:
        robot.v_straight = 0
        robot.v_curve += 0.1

def init_motor(robot):
    """Set speed to the motors."""

    robot.motor.setMotor(robot.v_g, robot.v_d)