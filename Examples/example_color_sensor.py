import time
import board
import adafruit_tcs34725

# Initialize I2C and TCS34725 sensor
i2c = board.I2C()
sensor = adafruit_tcs34725.TCS34725(i2c)

# Set gain and integration time for the sensor
# sensor.gain = adafruit_tcs34725.GAIN_4X
# sensor.integration_time = 100  # In milliseconds

try:
    while True:
        # Read color values
        r, g, b, c = sensor.color_raw
        temperature = sensor.color_temperature  # Optional: Estimate color temperature
        lux = sensor.lux  # Optional: Calculate brightness in lux

        # print(f"Raw RGB: R={r}, G={g}, B={b}, Clear={c}")
        # if temperature is not None:
        #     print(f"Color Temperature: {temperature:.2f} K")
        # print(f"Lux: {lux:.2f} lx")
        # print("--------------------------")

        isWhite = lambda sensor: sensor.lux > 3000 and min(sensor.color_raw) > 15
        isGreen = (
            lambda sensor: 1500 > sensor.lux > 500
            and max(sensor.color_raw[:-1]) == sensor.color_raw[1]
        )
        isRed = (
            lambda sensor: 1500 > sensor.lux > 500
            and max(sensor.color_raw[:-1]) == sensor.color_raw[0]
        )
        isBlack = lambda sensor: 500 > sensor.lux and max(sensor.color_raw[:-1]) < 5

        print(f"""isWhite: {isWhite(sensor)}
isGreen: {isGreen(sensor)}
isRed: {isRed(sensor)}
isBlack: {isBlack(sensor)}""")

        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting...")
