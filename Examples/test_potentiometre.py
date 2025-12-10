from grove.adc import ADC
import lgpio as GPIO
import time

adc = ADC()


# Set function to calculate percent from angle
def angle_to_percent(angle):
    if angle > 180 or angle < 0:
        return False

    start = 4
    end = 12.5
    ratio = (end - start) / 180  # Calculate ratio from angle to percent

    angle_as_percent = angle * ratio

    return start + angle_as_percent


# Initialize GPIO chip
chip = GPIO.gpiochip_open(0)  # Open GPIO chip (usually 0 for Raspberry Pi)

# Use GPIO3 (physical pin 5 on Raspberry Pi)
pwm_gpio = 3  # GPIO3 (BCM numbering, corresponds to BOARD pin 5)
frequency = 50  # PWM frequency in Hz
GPIO.gpio_claim_output(chip, pwm_gpio)

# Initialize PWM
GPIO.tx_pwm(chip, pwm_gpio, frequency, angle_to_percent(0))  # Init at 0°

try:
    while True:
        time.sleep(0.1)
        value = adc.read(0)  # Read potentiometer on A0
        angle = int((value / 999) * 180)  # Convert value to angle (0-180 degrees)
        duty_cycle = angle_to_percent(angle)
        if duty_cycle is not False:
            GPIO.tx_pwm(chip, pwm_gpio, frequency, duty_cycle)
            print("Valeur potentiomètre:", value)
        else:
            print("Angle hors limites:", angle)
except KeyboardInterrupt:
    print("Programme terminé")
finally:
    GPIO.tx_pwm(chip, pwm_gpio, frequency, 0)  # Stop PWM
    GPIO.gpiochip_close(chip)  # Close GPIO chip
