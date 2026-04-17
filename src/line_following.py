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

    if self.color_l.isGreen() and self.color_r.isGreen():
        print("u turn")
        self.u_turn()
    elif self.color_l.isGreen():
        print("turn l")
        self.ninety_turn(-1)
    elif self.color_r.isGreen():
        print("turn r")
        self.ninety_turn(1)
    elif self.color_l.isRed() or self.color_r.isRed():
        print("mode arena")
        self.mode = "arena"

def dodge_obstacle(self):
    """Dodge a detected obstacle."""
    t = 0.2
    
    self.ninety_turn(1)
    self.motor.setMotor(20,20)
    time.sleep(t)
    self.motor.setMotor(0,0)
    
    self.ninety_turn(-1)
    self.motor.setMotor(20,20)
    time.sleep(t)
    self.motor.setMotor(0,0)
    
    self.ninety_turn(-1)
    self.motor.setMotor(20,20)
    time.sleep(t)
    self.motor.setMotor(0,0)
    
    self.ninety_turn(1)
    self.motor.setMotor(20,20)
    time.sleep(t)
    self.motor.setMotor(0,0)
    
    

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