import RPi.GPIO as GPIO
import time


class AlphaBotLineSensor(object):
    def __init__(self, numSensors=5):
        self.CS = 5
        self.Clock = 25
        self.Address = 24
        self.DataOut = 23

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.Clock, GPIO.OUT)
        GPIO.setup(self.Address, GPIO.OUT)
        GPIO.setup(self.CS, GPIO.OUT)
        GPIO.setup(self.DataOut, GPIO.IN, GPIO.PUD_UP)

        self.numSensors = numSensors
        self.calibratedMin = [0] * self.numSensors
        self.calibratedMax = [1023] * self.numSensors
        self.last_value = 0

    """
	Reads the sensor values into an array. There *MUST* be space
	for as many values as there were sensors specified in the constructor.
	Example usage:
	unsigned int sensor_values[8];
	sensors.read(sensor_values);
	The values returned are a measure of the reflectance in abstract units,
	with higher values corresponding to lower reflectance (e.g. a black
	surface or a void).
	"""

    def AnalogRead(self):
        value = [0] * 6
        for j in range(0, 6):
            GPIO.output(self.CS, GPIO.LOW)
            time.sleep(0.00001)

            # Envoi de l'adresse (4 bits)
            for i in range(0, 4):
                if ((j) >> (3 - i)) & 0x01:
                    GPIO.output(self.Address, GPIO.HIGH)
                else:
                    GPIO.output(self.Address, GPIO.LOW)

                # On lit la donnée entrante pendant qu'on envoie l'adresse
                GPIO.output(self.Clock, GPIO.HIGH)
                value[j] <<= 1
                if GPIO.input(self.DataOut):
                    value[j] |= 0x01
                GPIO.output(self.Clock, GPIO.LOW)

            # Lecture des 6 bits restants (pour faire 10 bits total)
            for i in range(0, 6):
                GPIO.output(self.Clock, GPIO.HIGH)
                value[j] <<= 1
                if GPIO.input(self.DataOut):
                    value[j] |= 0x01
                GPIO.output(self.Clock, GPIO.LOW)

            # Cycle de fin pour laisser la puce respirer
            for i in range(0, 6):
                GPIO.output(self.Clock, GPIO.HIGH)
                GPIO.output(self.Clock, GPIO.LOW)

            GPIO.output(self.CS, GPIO.HIGH)
            time.sleep(0.0001)

        return value[1:]

    """
	Reads the sensors 10 times and uses the results for
	calibration.  The sensor values are not returned; instead, the
	maximum and minimum values found over time are stored internally
	and used for the readCalibrated() method.
	"""

    def calibrate(self):
        max_sensor_values = [0] * self.numSensors
        min_sensor_values = [0] * self.numSensors
        for j in range(0, 10):
            sensor_values = self.AnalogRead()

            for i in range(0, self.numSensors):
                # set the max we found THIS time
                if (j == 0) or max_sensor_values[i] < sensor_values[i]:
                    max_sensor_values[i] = sensor_values[i]

                # set the min we found THIS time
                if (j == 0) or min_sensor_values[i] > sensor_values[i]:
                    min_sensor_values[i] = sensor_values[i]

        # record the min and max calibration values
        for i in range(0, self.numSensors):
            if min_sensor_values[i] > self.calibratedMin[i]:
                self.calibratedMin[i] = min_sensor_values[i]
            if max_sensor_values[i] < self.calibratedMax[i]:
                self.calibratedMax[i] = max_sensor_values[i]

    """
	Returns values calibrated to a value between 0 and 1000, where
	0 corresponds to the minimum value read by calibrate() and 1000
	corresponds to the maximum value.  Calibration values are
	stored separately for each sensor, so that differences in the
	sensors are accounted for automatically.
	"""

    def readCalibrated(self):
        value = 0
        # read the needed values
        sensor_values = self.AnalogRead()

        for i in range(0, self.numSensors):
            denominator = self.calibratedMax[i] - self.calibratedMin[i]

            if denominator != 0:
                value = (sensor_values[i] - self.calibratedMin[i]) * 1000 / denominator

            if value < 0:
                value = 0
            elif value > 1000:
                value = 1000

            sensor_values[i] = value

        return sensor_values
